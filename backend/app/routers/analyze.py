"""Video analysis API routes."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request

from app.models import AnalyzeRequest, AnalyzeResponse
from app.services.analyzer import video_analyzer
from app.utils.helpers import normalize_youtube_url
from app.utils.rate_limit import rate_limiter

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("", response_model=AnalyzeResponse)
async def analyze_video(payload: AnalyzeRequest, request: Request) -> AnalyzeResponse:
    rate_limiter.enforce(request)
    try:
        normalized = normalize_youtube_url(str(payload.url))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        return await video_analyzer.analyze(normalized)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Failed to analyze video: {exc}") from exc
