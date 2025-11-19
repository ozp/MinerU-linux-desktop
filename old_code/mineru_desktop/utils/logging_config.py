"""
Logging configuration module.

Provides structured logging setup for the entire application.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_format: Optional[str] = None
) -> None:
    """
    Configure application-wide logging.

    Args:
        level: Logging level (default: INFO)
        log_file: Optional path to log file
        log_format: Optional custom log format

    Example:
        >>> setup_logging(level=logging.DEBUG)
    """
    if log_format is None:
        log_format = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )

    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=_get_handlers(log_file, log_format)
    )

    # Set third-party loggers to WARNING to reduce noise
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)


def _get_handlers(
    log_file: Optional[str],
    log_format: str
) -> list:
    """
    Create logging handlers.

    Args:
        log_file: Optional path to log file
        log_format: Log format string

    Returns:
        List of logging handlers
    """
    formatter = logging.Formatter(log_format)
    handlers = []

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    handlers.append(console_handler)

    # File handler (optional)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    return handlers


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name for the logger (typically __name__)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return logging.getLogger(name)
