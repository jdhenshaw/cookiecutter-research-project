"""Logging configuration and setup.

This module provides functions for configuring logging for the phangs_scouse
package, including console and file handlers with customizable formats.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def setup_logging(
    level: int | str = logging.INFO,
    format_string: str | None = None,
    log_file: Path | str | None = None,
) -> None:
    """Configure logging for phangs_scouse.

    Parameters
    ----------
    level : int | str, optional
        Logging level (DEBUG, INFO, WARNING, ERROR). Defaults to INFO.
    format_string : str | None, optional
        Custom format string. If None, uses a default format.
    log_file : Path | str | None, optional
        Optional log file path. If None, logs only to stderr.
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)

    logger = logging.getLogger("phangs_scouse")
    logger.setLevel(level)

    logger.handlers.clear()

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Get a logger for a specific module.

    Parameters
    ----------
    name : str
        Logger name (typically __name__).

    Returns
    -------
    logging.Logger
        The logger instance.
    """
    return logging.getLogger(f"phangs_scouse.{name}")
