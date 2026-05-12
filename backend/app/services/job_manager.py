"""In-memory download job orchestration with queue and lifecycle controls."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Awaitable, Callable

from app.config import MAX_PARALLEL_JOBS
from app.models import HistoryEntry, JobProgress, JobStatus
from app.utils.helpers import now_ts

logger = logging.getLogger(__name__)

JobHandler = Callable[["JobRecord"], Awaitable[None]]


@dataclass
class JobRecord:
    job_id: str
    url: str
    title: str | None = None
    format: str = "mp4"
    quality: str = "best"
    status: JobStatus = JobStatus.QUEUED
    progress: float = 0.0
    speed: str | None = None
    eta: str | None = None
    downloaded_bytes: int | None = None
    total_bytes: int | None = None
    filename: str | None = None
    file_path: Path | None = None
    error: str | None = None
    retries: int = 0
    created_at: float = field(default_factory=now_ts)
    updated_at: float = field(default_factory=now_ts)
    pause_event: asyncio.Event = field(default_factory=asyncio.Event)
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event)
    thumbnail: str | None = None
    client_id: str = "anonymous"

    def __post_init__(self) -> None:
        self.pause_event.set()

    def to_progress(self) -> JobProgress:
        return JobProgress(
            job_id=self.job_id,
            status=self.status,
            progress=round(self.progress, 2),
            speed=self.speed,
            eta=self.eta,
            downloaded_bytes=self.downloaded_bytes,
            total_bytes=self.total_bytes,
            filename=self.filename,
            error=self.error,
            retries=self.retries,
            format=self.format,
            quality=self.quality,
            title=self.title,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    def to_history(self) -> HistoryEntry:
        return HistoryEntry(
            id=self.job_id,
            url=self.url,
            title=self.title or "Unknown title",
            format=self.format,
            quality=self.quality,
            status=self.status,
            filename=self.filename,
            completed_at=self.updated_at if self.status == JobStatus.COMPLETED else None,
            thumbnail=self.thumbnail,
        )


class JobManager:
    def __init__(self, max_parallel: int) -> None:
        self.max_parallel = max_parallel
        self._jobs: dict[str, JobRecord] = {}
        self._queue: asyncio.Queue[str] = asyncio.Queue()
        self._handlers: dict[str, JobHandler] = {}
        self._workers_started = False
        self._lock = asyncio.Lock()

    def register_handler(self, format_name: str, handler: JobHandler) -> None:
        self._handlers[format_name] = handler

    async def start_workers(self) -> None:
        if self._workers_started:
            return
        self._workers_started = True
        for _ in range(self.max_parallel):
            asyncio.create_task(self._worker())

    async def create_job(
        self,
        *,
        url: str,
        format_name: str,
        quality: str,
        client_id: str,
        title: str | None = None,
        thumbnail: str | None = None,
    ) -> JobRecord:
        job_id = str(uuid.uuid4())
        job = JobRecord(
            job_id=job_id,
            url=url,
            title=title,
            format=format_name,
            quality=quality,
            client_id=client_id,
            thumbnail=thumbnail,
        )
        async with self._lock:
            self._jobs[job_id] = job
        await self._queue.put(job_id)
        await self.start_workers()
        return job

    async def get_job(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)

    async def update_job(self, job_id: str, **fields: Any) -> JobRecord | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        for key, value in fields.items():
            if hasattr(job, key):
                setattr(job, key, value)
        job.updated_at = now_ts()
        return job

    async def pause_job(self, job_id: str) -> JobRecord | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.pause_event.clear()
        job.status = JobStatus.PAUSED
        job.updated_at = now_ts()
        return job

    async def resume_job(self, job_id: str) -> JobRecord | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.pause_event.set()
        if job.status == JobStatus.PAUSED:
            job.status = JobStatus.DOWNLOADING
        job.updated_at = now_ts()
        return job

    async def cancel_job(self, job_id: str) -> JobRecord | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.cancel_event.set()
        job.pause_event.set()
        job.status = JobStatus.CANCELLED
        job.updated_at = now_ts()
        return job

    async def list_history(self, client_id: str | None = None, limit: int = 50) -> list[HistoryEntry]:
        jobs = list(self._jobs.values())
        if client_id:
            jobs = [job for job in jobs if job.client_id == client_id]
        jobs.sort(key=lambda item: item.updated_at, reverse=True)
        return [job.to_history() for job in jobs[:limit]]

    async def active_count(self) -> tuple[int, int]:
        active = sum(
            1
            for job in self._jobs.values()
            if job.status in {JobStatus.DOWNLOADING, JobStatus.PROCESSING, JobStatus.ANALYZING}
        )
        queued = sum(1 for job in self._jobs.values() if job.status == JobStatus.QUEUED)
        return active, queued

    async def _worker(self) -> None:
        while True:
            job_id = await self._queue.get()
            job = self._jobs.get(job_id)
            if not job:
                self._queue.task_done()
                continue
            if job.cancel_event.is_set():
                self._queue.task_done()
                continue

            handler = self._handlers.get(job.format)
            if not handler:
                await self.update_job(job_id, status=JobStatus.FAILED, error="Unsupported format handler.")
                self._queue.task_done()
                continue

            try:
                await handler(job)
            except asyncio.CancelledError:
                await self.update_job(job_id, status=JobStatus.CANCELLED)
                raise
            except Exception as exc:  # noqa: BLE001
                logger.exception("Job %s failed", job_id)
                await self.update_job(job_id, status=JobStatus.FAILED, error=str(exc))
            finally:
                self._queue.task_done()


job_manager = JobManager(MAX_PARALLEL_JOBS)
