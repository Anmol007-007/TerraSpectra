"""Structured logging configuration for TerraSpectra."""

from __future__ import annotations

import logging
import sys
from typing import Any

from rich.console import Console
from rich.logging import RichHandler


def setup_logging(
    level: str | int = logging.INFO,
    json_format: bool = False,
    log_file: str | None = None,
) -> logging.Logger:
    """Configure structured root logger with console and optional file handler.

    Args:
        level: Logging level (e.g. logging.INFO or "INFO").
        json_format: If True, format records as JSON (for production/cloud).
        log_file: Optional filepath to write log stream to.

    Returns:
        Configured logger instance.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger("terraspectra")
    root.setLevel(level)
    root.handlers.clear()

    if not json_format:
        rich_handler = RichHandler(
            console=Console(file=sys.stderr),
            show_time=True,
            show_path=False,
            rich_tracebacks=True,
            markup=True,
        )
        rich_handler.setLevel(level)
        root.addHandler(rich_handler)
    else:
        stream_handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            '{"time":"%(asctime)s","name":"%(name)s","level":"%(levelname)s","message":"%(message)s"}'
        )
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        root.addHandler(stream_handler)

    if log_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(level)
        root.addHandler(file_handler)

    return root


logger: logging.Logger = setup_logging()
