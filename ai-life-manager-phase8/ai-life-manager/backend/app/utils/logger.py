"""Shared logging setup used across the app (never logs secrets — see mcp/logging.py)."""

import logging

from app.config import get_settings

_configured = False


def _configure_root_logger() -> None:
    global _configured
    if _configured:
        return
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure_root_logger()
    return logging.getLogger(name)
