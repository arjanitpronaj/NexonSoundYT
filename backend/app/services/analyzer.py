"""YouTube metadata extraction via yt-dlp."""

from __future__ import annotations

import asyncio
from typing import Any

import yt_dlp

from app.models import AnalyzeResponse, FormatInfo
from app.utils.helpers import estimate_size_for_quality, normalize_youtube_url, parse_upload_date


class VideoAnalyzer:
    def __init__(self) -> None:
        self._base_opts: dict[str, Any] = {
            "quiet": True,
            "no_warnings": True,
            "noplaylist": True,
            "skip_download": True,
            "socket_timeout": 30,
        }

    async def analyze(self, url: str) -> AnalyzeResponse:
        normalized = normalize_youtube_url(url)
        info = await asyncio.to_thread(self._extract_info, normalized)
        return self._build_response(normalized, info)

    def _extract_info(self, url: str) -> dict[str, Any]:
        with yt_dlp.YoutubeDL(self._base_opts) as ydl:
            return ydl.extract_info(url, download=False)

    def _build_response(self, url: str, info: dict[str, Any]) -> AnalyzeResponse:
        formats = info.get("formats") or []
        format_items: list[FormatInfo] = []
        seen: set[tuple[int | None, str]] = set()

        for fmt in formats:
            if fmt.get("vcodec") in (None, "none"):
                continue
            height = fmt.get("height")
            ext = fmt.get("ext") or "mp4"
            key = (height, ext)
            if key in seen:
                continue
            seen.add(key)
            format_items.append(
                FormatInfo(
                    quality=f"{height}p" if height else "unknown",
                    ext=ext,
                    filesize=fmt.get("filesize"),
                    filesize_approx=fmt.get("filesize_approx"),
                    vcodec=fmt.get("vcodec"),
                    acodec=fmt.get("acodec"),
                    fps=fmt.get("fps"),
                    height=height,
                    width=fmt.get("width"),
                )
            )

        format_items.sort(key=lambda item: item.height or 0, reverse=True)
        estimated_sizes = {
            quality: estimate_size_for_quality(info, quality)
            for quality in ["360p", "480p", "720p", "1080p", "2k", "4k", "best"]
        }

        return AnalyzeResponse(
            url=url,
            title=info.get("title") or "Untitled",
            channel=info.get("uploader") or info.get("channel") or "Unknown channel",
            upload_date=parse_upload_date(info.get("upload_date")),
            duration=int(info.get("duration") or 0),
            thumbnail=info.get("thumbnail"),
            description=info.get("description"),
            view_count=info.get("view_count"),
            formats=format_items,
            estimated_sizes=estimated_sizes,
        )


video_analyzer = VideoAnalyzer()
