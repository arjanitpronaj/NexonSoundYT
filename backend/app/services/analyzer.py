"""YouTube metadata extraction via yt-dlp."""

from __future__ import annotations

import asyncio
import json
import logging
import urllib.parse
import urllib.request
from typing import Any

import yt_dlp

from app.models import AnalyzeResponse, FormatInfo
from app.utils.helpers import estimate_size_for_quality, normalize_youtube_url, parse_upload_date
from app.utils.ytdlp_config import YOUTUBE_PLAYER_CLIENTS, build_ytdlp_options

logger = logging.getLogger(__name__)


class VideoAnalyzer:
    async def analyze(self, url: str) -> AnalyzeResponse:
        normalized = normalize_youtube_url(url)
        try:
            info = await asyncio.to_thread(self._extract_info, normalized)
            return self._build_response(normalized, info)
        except Exception as exc:  # noqa: BLE001
            logger.warning("yt-dlp analyze failed for %s: %s", normalized, exc)
            return await asyncio.to_thread(self._analyze_with_oembed, normalized)

    def _extract_info(self, url: str) -> dict[str, Any]:
        last_error: Exception | None = None
        for clients in YOUTUBE_PLAYER_CLIENTS:
            options = build_ytdlp_options(player_clients=clients, skip_download=True)
            try:
                with yt_dlp.YoutubeDL(options) as ydl:
                    return ydl.extract_info(url, download=False)
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                continue
        if last_error:
            raise last_error
        raise RuntimeError("Unable to analyze video.")

    def _analyze_with_oembed(self, url: str) -> AnalyzeResponse:
        endpoint = f"https://www.youtube.com/oembed?url={urllib.parse.quote(url, safe='')}&format=json"
        request = urllib.request.Request(endpoint, headers={"User-Agent": "NexonSoundYT/1.0"})
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.loads(response.read().decode("utf-8"))

        thumbnail = payload.get("thumbnail_url")
        formats = [
            FormatInfo(quality="360p", ext="mp4", height=360),
            FormatInfo(quality="480p", ext="mp4", height=480),
            FormatInfo(quality="720p", ext="mp4", height=720),
            FormatInfo(quality="1080p", ext="mp4", height=1080),
            FormatInfo(quality="best", ext="mp4"),
        ]
        estimated_sizes = {quality: None for quality in ["360p", "480p", "720p", "1080p", "2k", "4k", "best"]}

        return AnalyzeResponse(
            url=url,
            title=payload.get("title") or "Untitled",
            channel=payload.get("author_name") or "Unknown channel",
            upload_date=None,
            duration=0,
            thumbnail=thumbnail,
            description=None,
            view_count=None,
            formats=formats,
            estimated_sizes=estimated_sizes,
        )

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
