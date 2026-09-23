import argparse
import time
from concurrent.futures import ThreadPoolExecutor

from taskforge.config import get_settings
from taskforge.db import create_db_engine, create_session_factory
from taskforge.jobs import run_one_export


def run_worker(*, once: bool = False, poll_seconds: float = 1.0) -> None:
    settings = get_settings()
    engine = create_db_engine(settings)
    session_factory = create_session_factory(engine)
    try:
        with ThreadPoolExecutor(max_workers=settings.worker_concurrency) as pool:
            while True:
                results = list(
                    pool.map(
                        lambda _worker: run_one_export(
                            session_factory,
                            settings.export_storage_dir,
                            settings.job_lease_seconds,
                        ),
                        range(settings.worker_concurrency),
                    )
                )
                if once:
                    return
                if not any(results):
                    time.sleep(poll_seconds)
    finally:
        engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the TaskForge export worker")
    parser.add_argument(
        "--once",
        action="store_true",
        help="run one bounded claim batch and exit",
    )
    args = parser.parse_args()
    run_worker(once=args.once)


if __name__ == "__main__":
    main()
