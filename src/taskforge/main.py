import json
import logging
import time
from collections.abc import AsyncIterator, Callable
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, Request, Response, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis import Redis
from starlette.exceptions import HTTPException as StarletteHTTPException

from taskforge.api import router
from taskforge.cache import RedisProjectSummaryCache
from taskforge.config import Settings, get_settings
from taskforge.db import create_db_engine, create_session_factory
from taskforge.rate_limit import NullRateLimiter, RedisRateLimiter
from taskforge.services import TaskForgeService
from taskforge.store import InMemoryStore

logger = logging.getLogger("taskforge.api")


def configure_logging(level: str) -> None:
    logging.basicConfig(level=level, format="%(message)s")
    logger.setLevel(level)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(settings.log_level)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        yield
        engine = getattr(app.state, "engine", None)
        if engine is not None:
            engine.dispose()
        redis_client = getattr(app.state, "redis_client", None)
        if redis_client is not None:
            redis_client.close()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.state.settings = settings

    redis_client = Redis.from_url(
        settings.redis_url,
        socket_connect_timeout=settings.redis_timeout_seconds,
        socket_timeout=settings.redis_timeout_seconds,
        decode_responses=True,
    )
    app.state.redis_client = redis_client
    app.state.project_summary_cache = RedisProjectSummaryCache(
        redis_client,
        settings.project_summary_cache_ttl_seconds,
    )
    if settings.environment == "test":
        app.state.rate_limiter = NullRateLimiter()
    else:
        app.state.rate_limiter = RedisRateLimiter(redis_client)

    if settings.storage_backend == "postgres":
        engine = create_db_engine(settings)
        app.state.engine = engine
        app.state.session_factory = create_session_factory(engine)
    else:
        app.state.store = InMemoryStore()
        app.state.service = TaskForgeService(app.state.store)

    @app.middleware("http")
    async def request_context_middleware(
        request: Request,
        call_next: Callable[[Request], Response],
    ) -> Response:
        request_id = request.headers.get("X-Request-ID", str(uuid4()))
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            json.dumps(
                {
                    "event": "http_request",
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
                separators=(",", ":"),
            )
        )
        return response

    @app.exception_handler(StarletteHTTPException)
    def http_exception_handler(
        _request: Request,
        exc: StarletteHTTPException,
    ) -> JSONResponse:
        detail = exc.detail
        if isinstance(detail, dict) and "code" in detail and "message" in detail:
            error = detail
        else:
            error = {"code": "http_error", "message": str(detail)}
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": error},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(RequestValidationError)
    def validation_exception_handler(
        _request: Request,
        exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content={
                "error": {
                    "code": "validation_error",
                    "message": "Request validation failed",
                    "details": jsonable_encoder(exc.errors()),
                }
            },
        )

    @app.get("/health/live", tags=["health"])
    def live() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(router)
    return app


app = create_app()
