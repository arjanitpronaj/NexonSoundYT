"""Job status, queue controls, and history routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.models import HealthResponse, HistoryResponse, JobProgress, JobStatus
from app.services.job_manager import job_manager
from app.utils.rate_limit import rate_limiter

router = APIRouter(tags=["status"])


def _client_id(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "anonymous"


@router.get("/status/{job_id}", response_model=JobProgress)
async def get_status(job_id: str, request: Request) -> JobProgress:
    rate_limiter.enforce(request)
    job = await job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job.to_progress()


@router.post("/status/{job_id}/pause", response_model=JobProgress)
async def pause_job(job_id: str, request: Request) -> JobProgress:
    rate_limiter.enforce(request)
    job = await job_manager.pause_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job.to_progress()


@router.post("/status/{job_id}/resume", response_model=JobProgress)
async def resume_job(job_id: str, request: Request) -> JobProgress:
    rate_limiter.enforce(request)
    job = await job_manager.resume_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job.to_progress()


@router.post("/status/{job_id}/cancel", response_model=JobProgress)
async def cancel_job(job_id: str, request: Request) -> JobProgress:
    rate_limiter.enforce(request)
    job = await job_manager.cancel_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job.to_progress()


@router.get("/history", response_model=HistoryResponse)
async def get_history(request: Request, limit: int = 50) -> HistoryResponse:
    rate_limiter.enforce(request)
    items = await job_manager.list_history(client_id=_client_id(request), limit=min(limit, 100))
    return HistoryResponse(items=items)


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    active, queued = await job_manager.active_count()
    return HealthResponse(status="ok", version="1.0.0", active_jobs=active, queued_jobs=queued)
