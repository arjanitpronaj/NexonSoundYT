"""Shared utility helpers."""

from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlparse

YOUTUBE_HOSTS = {
    "youtube.com",
    "www.youtube.com",
    "m.youtube.com",
    "music.youtube.com",
    "youtu.be",
    "www.youtu.be",
}


def now_ts() -> float:
    return time.time()


def format_bytes(num: int | float | None) -> str:
    if num is None:
        return "0 B"
    value = float(num)
    units = ["B", "KB", "MB", "GB", "TB"]
    for unit in units:
        if value < 1024.0 or unit == units[-1]:
            return f"{value:.1f} {unit}"
        value /= 1024.0
    return f"{value:.1f} TB"


def format_speed(speed: float | None) -> str | None:
    if speed is None or speed <= 0:
        return None
    return f"{format_bytes(speed)}/s"


def format_eta(seconds: float | None) -> str | None:
    if seconds is None or seconds <= 0:
        return None
    seconds = int(seconds)
    minutes, sec = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}h {minutes}m {sec}s"
    if minutes:
        return f"{minutes}m {sec}s"
    return f"{sec}s"


def normalize_youtube_url(url: str) -> str:
    parsed = urlparse(url.strip())
    host = parsed.netloc.lower().removeprefix("www.")
    if host not in {h.removeprefix("www.") for h in YOUTUBE_HOSTS}:
        raise ValueError("Only YouTube URLs are supported.")

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
        if not video_id:
            raise ValueError("Invalid YouTube short URL.")
        return f"https://www.youtube.com/watch?v={video_id}"

    if host in {"youtube.com", "music.youtube.com", "m.youtube.com"}:
        if parsed.path == "/watch":
            query = parse_qs(parsed.query)
            video_id = query.get("v", [None])[0]
            if not video_id:
                raise ValueError("Missing YouTube video id.")
            return f"https://www.youtube.com/watch?v={video_id}"
        match = re.match(r"^/(shorts|embed|live)/([^/?#]+)", parsed.path)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(2)}"

    raise ValueError("Unsupported YouTube URL format.")


def is_valid_youtube_url(url: str) -> bool:
    try:
        normalize_youtube_url(url)
        return True
    except ValueError:
        return False


def parse_upload_date(value: str | None) -> str | None:
    if not value:
        return None
    if re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%d")
    return value


def safe_filename(name: str, ext: str) -> str:
    cleaned = re.sub(r'[<>:"/\\|?*]+', "", name).strip().strip(".")
    cleaned = re.sub(r"\s+", " ", cleaned)[:180] or "download"
    return f"{cleaned}.{ext.lstrip('.')}"


def pick_format_by_height(formats: list[dict[str, Any]], target_height: int) -> dict[str, Any] | None:
    video_formats = [
        fmt
        for fmt in formats
        if fmt.get("vcodec") not in (None, "none")
        and fmt.get("height")
        and fmt.get("ext") in {"mp4", "webm", "mkv"}
    ]
    if not video_formats:
        return None
    exact = [fmt for fmt in video_formats if int(fmt.get("height", 0)) == target_height]
    if exact:
        return sorted(exact, key=lambda item: item.get("tbr") or 0, reverse=True)[0]
    lower = [fmt for fmt in video_formats if int(fmt.get("height", 0)) <= target_height]
    if lower:
        return sorted(lower, key=lambda item: item.get("height", 0), reverse=True)[0]
    return sorted(video_formats, key=lambda item: item.get("height", 0))[0]


def estimate_size_for_quality(info: dict[str, Any], quality: str) -> int | None:
    formats = info.get("formats") or []
    if quality == "best":
        sizes = [fmt.get("filesize") or fmt.get("filesize_approx") for fmt in formats if fmt.get("vcodec") != "none"]
        sizes = [size for size in sizes if size]
        return max(sizes) if sizes else info.get("filesize") or info.get("filesize_approx")

    height_map = {
        "360p": 360,
        "480p": 480,
        "720p": 720,
        "1080p": 1080,
        "2k": 1440,
        "4k": 2160,
    }
    target = height_map.get(quality)
    if not target:
        return None
    selected = pick_format_by_height(formats, target)
    if not selected:
        return None
    return selected.get("filesize") or selected.get("filesize_approx")
