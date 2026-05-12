"""Background cleanup for temporary download artifacts."""

from __future__ import annotations

import asyncio
import logging
import shutil
import time
from pathlib import Path

from app.config import JOB_TTL_SECONDS, TEMP_DIR

logger = logging.getLogger(__name__)


class TempFileCleaner:
    def __init__(self, temp_dir: Path, ttl_seconds: int) -> None:
        self.temp_dir = temp_dir
        self.ttl_seconds = ttl_seconds
        self._task: asyncio.Task | None = None

    async def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._loop())

    async def stop(self) -> None:
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
            self._task = None

    async def _loop(self) -> None:
        while True:
            try:
                self.cleanup_expired()
            except Exception:  # noqa: BLE001
                logger.exception("Temp cleanup failed")
            await asyncio.sleep(300)

    def cleanup_expired(self) -> None:
        if not self.temp_dir.exists():
            return
        cutoff = time.time() - self.ttl_seconds
        for path in self.temp_dir.iterdir():
            try:
                if path.is_dir():
                    if path.stat().st_mtime < cutoff:
                        shutil.rmtree(path, ignore_errors=True)
                elif path.is_file() and path.stat().st_mtime < cutoff:
                    path.unlink(missing_ok=True)
            except OSError:
                logger.warning("Failed to remove temp path %s", path)

    def remove_path(self, path: Path | None) -> None:
        if not path:
            return
        try:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            elif path.exists():
                path.unlink(missing_ok=True)
        except OSError:
            logger.warning("Failed to remove path %s", path)


temp_cleaner = TempFileCleaner(TEMP_DIR, JOB_TTL_SECONDS)
