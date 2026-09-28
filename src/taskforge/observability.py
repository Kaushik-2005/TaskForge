from collections import Counter
from dataclasses import dataclass, field


@dataclass
class HttpMetrics:
    request_count: Counter[tuple[str, str, str]] = field(default_factory=Counter)
    duration_buckets: Counter[tuple[str, str, str, str]] = field(
        default_factory=Counter
    )

    def record(
        self,
        method: str,
        route: str,
        status_class: str,
        duration_ms: float,
    ) -> None:
        self.request_count[(method, route, status_class)] += 1
        bucket = self._bucket(duration_ms)
        self.duration_buckets[(method, route, status_class, bucket)] += 1

    @staticmethod
    def _bucket(duration_ms: float) -> str:
        if duration_ms <= 100:
            return "le_100ms"
        if duration_ms <= 500:
            return "le_500ms"
        if duration_ms <= 1000:
            return "le_1s"
        return "gt_1s"
