"""Download job creation and file delivery routes."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from app.models import DownloadMp3Request, DownloadMp4Request, JobCreateResponse, JobStatus
from app.services.job_manager import job_manager
from app.utils.helpers import normalize_youtube_url
from app.utils.rate_limit import rate_limiter

router = APIRouter(prefix="/download", tags=["download"])


def _client_id(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "anonymous"


@router.post("/mp4", response_model=JobCreateResponse)
async def download_mp4(payload: DownloadMp4Request, request: Request) -> JobCreateResponse:
    rate_limiter.enforce(request)
    try:
        normalized = normalize_youtube_url(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    job = await job_manager.create_job(
        url=normalized,
        format_name="mp4",
        quality=payload.quality.value,
        client_id=_client_id(request),
    )
    return JobCreateResponse(job_id=job.job_id, status=JobStatus.QUEUED)


@router.post("/mp3", response_model=JobCreateResponse)
async def download_mp3(payload: DownloadMp3Request, request: Request) -> JobCreateResponse:
    rate_limiter.enforce(request)
    try:
        normalized = normalize_youtube_url(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    quality = f"{payload.bitrate.value}kbps"
    job = await job_manager.create_job(
        url=normalized,
        format_name="mp3",
        quality=quality,
        client_id=_client_id(request),
    )
    return JobCreateResponse(job_id=job.job_id, status=JobStatus.QUEUED)


@router.get("/file/{job_id}")
async def download_file(job_id: str, request: Request):
    rate_limiter.enforce(request)
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    if job.status != JobStatus.COMPLETED or not job.file_path:
        raise HTTPException(status_code=409, detail="File is not ready yet.")

    file_path: Path = job.file_path
    if not file_path.exists():
        raise HTTPException(status_code=410, detail="File expired or was cleaned up.")

    media_type = "video/mp4" if job.format == "mp4" else "audio/mpeg"
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=job.filename or file_path.name,
    )
