from __future__ import annotations

import sys
from loguru import logger

from .settings import get_settings


def configure_logging() -> None:
    logger.remove()
    settings = get_settings()
    logger.add(
        sys.stdout,
        level=settings.platform.log_level,
        backtrace=False,
        diagnose=False,
        enqueue=True,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    )


def get_logger(name: str):
    return logger.bind(component=name)
