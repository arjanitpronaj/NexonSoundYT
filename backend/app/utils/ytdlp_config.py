"""Shared yt-dlp configuration for cloud and local extraction."""

from __future__ import annotations

from typing import Any

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.6778.200 Mobile Safari/537.36"
)

YOUTUBE_PLAYER_CLIENTS: list[list[str]] = [
    ["android", "web"],
    ["tv_embedded", "web"],
    ["ios", "web"],
    ["mweb", "web"],
]


def build_ytdlp_options(*, player_clients: list[str] | None = None, **overrides: Any) -> dict[str, Any]:
    options: dict[str, Any] = {
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 3,
        "fragment_retries": 3,
        "extractor_retries": 3,
        "user_agent": DEFAULT_USER_AGENT,
        "extractor_args": {
            "youtube": {
                "player_client": player_clients or YOUTUBE_PLAYER_CLIENTS[0],
            }
        },
    }
    options.update(overrides)
    return options
