"""In-memory per-client rate limiting."""

from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request

from app.config import RATE_LIMIT_PER_MINUTE


class RateLimiter:
    def __init__(self, limit_per_minute: int) -> None:
        self.limit_per_minute = limit_per_minute
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _client_key(self, request: Request) -> str:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
        if request.client:
            return request.client.host
        return "unknown"

    def enforce(self, request: Request) -> None:
        if self.limit_per_minute <= 0:
            return

        key = self._client_key(request)
        now = time.time()
        window_start = now - 60

        with self._lock:
            bucket = self._events[key]
            while bucket and bucket[0] < window_start:
                bucket.popleft()
            if len(bucket) >= self.limit_per_minute:
                raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again shortly.")
            bucket.append(now)


rate_limiter = RateLimiter(RATE_LIMIT_PER_MINUTE)
