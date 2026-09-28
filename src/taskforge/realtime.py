import asyncio
from collections import defaultdict
from uuid import UUID


class WorkspaceUpdateBroker:
    def __init__(self, queue_size: int = 10) -> None:
        if queue_size < 1:
            raise ValueError("queue_size must be positive")
        self.queue_size = queue_size
        self._subscribers: dict[UUID, set[asyncio.Queue[dict[str, object]]]] = (
            defaultdict(set)
        )
        self._loops: dict[
            asyncio.Queue[dict[str, object]], asyncio.AbstractEventLoop
        ] = {}

    def subscribe(self, workspace_id: UUID) -> asyncio.Queue[dict[str, object]]:
        queue: asyncio.Queue[dict[str, object]] = asyncio.Queue(self.queue_size)
        self._subscribers[workspace_id].add(queue)
        try:
            self._loops[queue] = asyncio.get_running_loop()
        except RuntimeError:
            pass
        return queue

    def unsubscribe(
        self,
        workspace_id: UUID,
        queue: asyncio.Queue[dict[str, object]],
    ) -> None:
        subscribers = self._subscribers.get(workspace_id)
        if subscribers is None:
            return
        subscribers.discard(queue)
        self._loops.pop(queue, None)
        if not subscribers:
            self._subscribers.pop(workspace_id, None)

    def publish(self, workspace_id: UUID, event: dict[str, object]) -> None:
        for queue in tuple(self._subscribers.get(workspace_id, ())):
            loop = self._loops.get(queue)
            if loop is not None and loop.is_running():
                loop.call_soon_threadsafe(
                    self._enqueue,
                    workspace_id,
                    queue,
                    event,
                )
            else:
                self._enqueue(workspace_id, queue, event)

    def _enqueue(
        self,
        workspace_id: UUID,
        queue: asyncio.Queue[dict[str, object]],
        event: dict[str, object],
    ) -> None:
        if queue.full():
            queue.get_nowait()
            queue.put_nowait(
                {
                    "type": "resync_required",
                    "workspace_id": str(workspace_id),
                }
            )
        else:
            queue.put_nowait(event)
