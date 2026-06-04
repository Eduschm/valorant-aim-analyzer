"""Shared logging configuration for all services."""

from __future__ import annotations

import logging
import os

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s %(levelname)s %(name)s %(message)s")


def _resolve_level(level: str | None = None) -> int:
    name = (level or LOG_LEVEL or "INFO").upper()
    return logging._nameToLevel.get(name, logging.INFO)


def configure_logging(level: str | None = None) -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    root.addHandler(handler)
    root.setLevel(_resolve_level(level))
    logging.captureWarnings(True)


def get_logger(name: str | None = None) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name if name else __name__)
