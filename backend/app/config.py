"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = Path(os.getenv("TEMP_DIR", BASE_DIR / "temp"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Comma-separated list of allowed frontend origins for CORS.
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,https://nexonsoundyt.vercel.app",
    ).split(",")
    if origin.strip()
]

# Maximum concurrent active download jobs per process.
MAX_PARALLEL_JOBS = int(os.getenv("MAX_PARALLEL_JOBS", "3"))

# Per-IP request rate limit (requests per minute).
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "30"))

# Auto-delete completed job artifacts after this many seconds.
JOB_TTL_SECONDS = int(os.getenv("JOB_TTL_SECONDS", "3600"))

# Retry failed downloads up to this many times.
MAX_DOWNLOAD_RETRIES = int(os.getenv("MAX_DOWNLOAD_RETRIES", "2"))

# FFmpeg binary name/path.
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

# yt-dlp binary name/path.
YTDLP_PATH = os.getenv("YTDLP_PATH", "yt-dlp")
