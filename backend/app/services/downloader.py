"""yt-dlp and FFmpeg download execution."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import Any

import yt_dlp

from app.config import FFMPEG_PATH, MAX_DOWNLOAD_RETRIES, TEMP_DIR
from app.models import JobStatus
from app.services.job_manager import JobRecord, job_manager
from app.utils.helpers import format_eta, format_speed, normalize_youtube_url, safe_filename

logger = logging.getLogger(__name__)

HEIGHT_MAP = {
    "360p": 360,
    "480p": 480,
    "720p": 720,
    "1080p": 1080,
    "2k": 1440,
    "4k": 2160,
}


class DownloadService:
    def __init__(self) -> None:
        self._loop: asyncio.AbstractEventLoop | None = None
        job_manager.register_handler("mp4", self.run_mp4_job)
        job_manager.register_handler("mp3", self.run_mp3_job)

    def bind_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def run_mp4_job(self, job: JobRecord) -> None:
        await self._run_with_retries(job, self._download_mp4)

    async def run_mp3_job(self, job: JobRecord) -> None:
        await self._run_with_retries(job, self._download_mp3)

    async def _run_with_retries(self, job: JobRecord, worker) -> None:
        while True:
            if job.cancel_event.is_set():
                await job_manager.update_job(job.job_id, status=JobStatus.CANCELLED)
                return
            try:
                await worker(job)
                return
            except JobCancelled:
                await job_manager.update_job(job.job_id, status=JobStatus.CANCELLED)
                return
            except Exception as exc:  # noqa: BLE001
                job.retries += 1
                await job_manager.update_job(
                    job.job_id,
                    retries=job.retries,
                    error=str(exc),
                    status=JobStatus.FAILED if job.retries > MAX_DOWNLOAD_RETRIES else JobStatus.QUEUED,
                )
                if job.retries > MAX_DOWNLOAD_RETRIES:
                    raise
                await asyncio.sleep(min(2 * job.retries, 8))

    async def _download_mp4(self, job: JobRecord) -> None:
        normalized = normalize_youtube_url(job.url)
        output_dir = TEMP_DIR / job.job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        await job_manager.update_job(job.job_id, status=JobStatus.DOWNLOADING, progress=0.0)

        def progress_hook(data: dict[str, Any]) -> None:
            loop = self._loop
            if loop is None:
                return
            asyncio.run_coroutine_threadsafe(self._handle_hook(job.job_id, data), loop)

        ydl_opts = self._base_opts(output_dir, progress_hook)
        ydl_opts["format"] = self._video_format_selector(job.quality)
        ydl_opts["merge_output_format"] = "mp4"
        ydl_opts["postprocessors"] = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]

        info, file_path = await asyncio.to_thread(self._execute_download, normalized, ydl_opts, output_dir, job)
        title = info.get("title") or job.title or "video"
        filename = safe_filename(title, "mp4")
        final_path = output_dir / filename
        if file_path != final_path:
            file_path.rename(final_path)

        await job_manager.update_job(
            job.job_id,
            status=JobStatus.COMPLETED,
            progress=100.0,
            filename=filename,
            file_path=final_path,
            title=title,
            thumbnail=info.get("thumbnail") or job.thumbnail,
        )

    async def _download_mp3(self, job: JobRecord) -> None:
        normalized = normalize_youtube_url(job.url)
        output_dir = TEMP_DIR / job.job_id
        output_dir.mkdir(parents=True, exist_ok=True)
        await job_manager.update_job(job.job_id, status=JobStatus.DOWNLOADING, progress=0.0)

        bitrate = job.quality.replace("kbps", "")

        def progress_hook(data: dict[str, Any]) -> None:
            loop = self._loop
            if loop is None:
                return
            asyncio.run_coroutine_threadsafe(self._handle_hook(job.job_id, data), loop)

        ydl_opts = self._base_opts(output_dir, progress_hook)
        ydl_opts["format"] = "bestaudio/best"
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": bitrate,
            },
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"},
        ]
        ydl_opts["writethumbnail"] = True

        info, file_path = await asyncio.to_thread(self._execute_download, normalized, ydl_opts, output_dir, job)
        title = info.get("title") or job.title or "audio"
        filename = safe_filename(title, "mp3")
        final_path = output_dir / filename
        if file_path.suffix.lower() != ".mp3":
            target = file_path.with_suffix(".mp3")
            if target.exists():
                file_path = target
        if file_path != final_path and file_path.exists():
            file_path.rename(final_path)
        elif not final_path.exists() and file_path.exists():
            final_path = file_path

        await job_manager.update_job(
            job.job_id,
            status=JobStatus.COMPLETED,
            progress=100.0,
            filename=final_path.name,
            file_path=final_path,
            title=title,
            thumbnail=info.get("thumbnail") or job.thumbnail,
        )

    def _base_opts(self, output_dir: Path, progress_hook) -> dict[str, Any]:
        return {
            "outtmpl": str(output_dir / "%(title).180B.%(ext)s"),
            "restrictfilenames": False,
            "noplaylist": True,
            "quiet": True,
            "no_warnings": True,
            "ffmpeg_location": FFMPEG_PATH,
            "progress_hooks": [progress_hook],
            "socket_timeout": 60,
            "retries": 3,
            "fragment_retries": 3,
            "paths": {"home": str(output_dir)},
        }

    def _video_format_selector(self, quality: str) -> str:
        if quality == "best":
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
        height = HEIGHT_MAP.get(quality)
        if not height:
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
        return (
            f"bestvideo[height<={height}][ext=mp4]+bestaudio[ext=m4a]/"
            f"bestvideo[height<={height}]+bestaudio/"
            f"best[height<={height}]"
        )

    def _execute_download(
        self,
        url: str,
        ydl_opts: dict[str, Any],
        output_dir: Path,
        job: JobRecord,
    ) -> tuple[dict[str, Any], Path]:
        with yt_dlp.YoutubeDL({**ydl_opts, "paths": {"home": str(output_dir)}}) as ydl:
            info = ydl.extract_info(url, download=True)
            if job.cancel_event.is_set():
                raise JobCancelled()
            file_path = Path(ydl.prepare_filename(info))
            if not file_path.exists():
                candidates = list(output_dir.glob("*"))
                media = [
                    path
                    for path in candidates
                    if path.is_file() and path.suffix.lower() in {".mp4", ".mp3", ".m4a", ".webm"}
                ]
                if not media:
                    raise RuntimeError("Download finished but output file was not found.")
                file_path = media[0]
            return info, file_path

    async def _handle_hook(self, job_id: str, data: dict[str, Any]) -> None:
        job = await job_manager.get_job(job_id)
        if not job:
            return
        if job.cancel_event.is_set():
            return
        await job.pause_event.wait()

        status = data.get("status")
        if status == "downloading":
            total = data.get("total_bytes") or data.get("total_bytes_estimate")
            downloaded = data.get("downloaded_bytes") or 0
            progress = (downloaded / total * 100) if total else job.progress
            await job_manager.update_job(
                job_id,
                status=JobStatus.DOWNLOADING,
                progress=min(progress, 99.0),
                downloaded_bytes=downloaded,
                total_bytes=total,
                speed=format_speed(data.get("speed")),
                eta=format_eta(data.get("eta")),
            )
        elif status == "finished":
            await job_manager.update_job(job_id, status=JobStatus.PROCESSING, progress=99.0)


class JobCancelled(Exception):
    pass


download_service = DownloadService()
