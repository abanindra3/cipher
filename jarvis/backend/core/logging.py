from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from jarvis.backend.core.config import settings


def configure_logging() -> None:
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    logging.basicConfig(level=settings.log_level.upper(), format=fmt)
    handler = RotatingFileHandler(log_dir / "jarvis.log", maxBytes=2_000_000, backupCount=5)
    handler.setFormatter(logging.Formatter(fmt))
    logging.getLogger().addHandler(handler)


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

