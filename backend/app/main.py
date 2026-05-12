"""NexonSoundYT FastAPI application entrypoint."""

from __future__ import annotations

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import CORS_ORIGINS
from app.routers import analyze, download, status
from app.services.downloader import download_service
from app.services.job_manager import job_manager
from app.utils.cleanup import temp_cleaner

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("nexonsoundyt")


@asynccontextmanager
async def lifespan(_: FastAPI):
    _ = download_service
    download_service.bind_loop(asyncio.get_running_loop())
    await job_manager.start_workers()
    await temp_cleaner.start()
    logger.info("NexonSoundYT backend started")
    try:
        yield
    finally:
        await temp_cleaner.stop()
        logger.info("NexonSoundYT backend stopped")


app = FastAPI(
    title="NexonSoundYT API",
    description="Production-ready YouTube downloader backend powered by FastAPI, yt-dlp, and FFmpeg.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router)
app.include_router(download.router)
app.include_router(status.router)


@app.get("/")
async def root():
    return {
        "name": "NexonSoundYT API",
        "docs": "/docs",
        "health": "/health",
    }
