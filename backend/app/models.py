"""Pydantic models for API request and response payloads."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, HttpUrl


class VideoQuality(str, Enum):
    Q360 = "360p"
    Q480 = "480p"
    Q720 = "720p"
    Q1080 = "1080p"
    Q2K = "2k"
    Q4K = "4k"
    BEST = "best"


class AudioBitrate(str, Enum):
    B128 = "128"
    B192 = "192"
    B320 = "320"


class JobStatus(str, Enum):
    QUEUED = "queued"
    ANALYZING = "analyzing"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class AnalyzeRequest(BaseModel):
    url: HttpUrl


class FormatInfo(BaseModel):
    quality: str
    ext: str
    filesize: int | None = None
    filesize_approx: int | None = None
    vcodec: str | None = None
    acodec: str | None = None
    fps: float | None = None
    height: int | None = None
    width: int | None = None


class AnalyzeResponse(BaseModel):
    url: str
    title: str
    channel: str
    upload_date: str | None = None
    duration: int
    thumbnail: str | None = None
    description: str | None = None
    view_count: int | None = None
    formats: list[FormatInfo]
    estimated_sizes: dict[str, int | None] = Field(default_factory=dict)


class DownloadMp4Request(BaseModel):
    url: HttpUrl
    quality: VideoQuality = VideoQuality.BEST


class DownloadMp3Request(BaseModel):
    url: HttpUrl
    bitrate: AudioBitrate = AudioBitrate.B192
    embed_thumbnail: bool = True
    embed_metadata: bool = True


class JobProgress(BaseModel):
    job_id: str
    status: JobStatus
    progress: float = 0.0
    speed: str | None = None
    eta: str | None = None
    downloaded_bytes: int | None = None
    total_bytes: int | None = None
    filename: str | None = None
    error: str | None = None
    retries: int = 0
    format: str | None = None
    quality: str | None = None
    title: str | None = None
    created_at: float
    updated_at: float


class JobCreateResponse(BaseModel):
    job_id: str
    status: JobStatus


class HistoryEntry(BaseModel):
    id: str
    url: str
    title: str
    format: str
    quality: str
    status: JobStatus
    filename: str | None = None
    completed_at: float | None = None
    thumbnail: str | None = None


class HistoryResponse(BaseModel):
    items: list[HistoryEntry]


class HealthResponse(BaseModel):
    status: str
    version: str
    active_jobs: int
    queued_jobs: int


class ErrorResponse(BaseModel):
    detail: str
    code: str | None = None
    meta: dict[str, Any] | None = None
