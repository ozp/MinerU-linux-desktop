"""
Logging Configuration for MinerU Desktop Client.

This module provides a centralized logging system to replace print() statements
throughout the application. Logs are written to both console and file with
appropriate formatting and rotation.
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..ui.console_panel import ConsolePanel


def setup_logging(
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 3
) -> logging.Logger:
    """
    Configure application-wide logging with console and file handlers.

    Args:
        level: Logging level (default: INFO)
        log_file: Path to log file (default: ~/.local/share/MinerU/mineru.log)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup log files to keep

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger("mineru")
    logger.setLevel(level)

    # Avoid duplicate handlers
    if logger.handlers:
        return logger

    # Console handler with color support
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation
    if log_file is None:
        log_dir = Path.home() / ".local" / "share" / "MinerU"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = str(log_dir / "mineru.log")

    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG)  # Always log DEBUG to file
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s (%(filename)s:%(lineno)d): %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.

    Args:
        name: Name of the logger (typically __name__ of the module)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return logging.getLogger(f"mineru.{name}")


class ConsolePanelHandler(logging.Handler):
    """
    Custom logging handler that redirects logs to ConsolePanel widget.

    This handler integrates the Python logging system with the UI console panel,
    allowing all log messages to be displayed in the application interface.
    """

    # Mapping of Python logging levels to ConsolePanel LogLevel constants
    LEVEL_MAP = {
        logging.DEBUG: "Debug",
        logging.INFO: "Info",
        logging.WARNING: "Warning",
        logging.ERROR: "Error",
        logging.CRITICAL: "Error",
    }

    def __init__(self, console_panel: "ConsolePanel") -> None:
        """
        Initialize the console panel handler.

        Args:
            console_panel: Reference to the ConsolePanel widget
        """
        super().__init__()
        self.console_panel = console_panel

        # Set formatter with timestamp and level
        formatter = logging.Formatter(
            fmt="%(message)s",  # ConsolePanel adds its own timestamp and level
            datefmt="%H:%M:%S"
        )
        self.setFormatter(formatter)

    def emit(self, record: logging.LogRecord) -> None:
        """
        Emit a log record to the console panel.

        Args:
            record: Log record to emit
        """
        try:
            # Format the message
            msg = self.format(record)

            # Map logging level to ConsolePanel level
            level = self.LEVEL_MAP.get(record.levelno, "Info")

            # Send to console panel
            if self.console_panel:
                self.console_panel.append_log(msg, level)

        except Exception:
            # Avoid infinite recursion if logging the error fails
            self.handleError(record)


def add_console_panel_handler(console_panel: "ConsolePanel", level: int = logging.DEBUG) -> None:
    """
    Add a console panel handler to the main logger.

    This function connects the logging system to the UI console panel,
    allowing all log messages to be displayed in the application.

    Args:
        console_panel: Reference to the ConsolePanel widget
        level: Minimum logging level to display in console (default: DEBUG)

    Example:
        >>> from ..ui.console_panel import ConsolePanel
        >>> console = ConsolePanel()
        >>> add_console_panel_handler(console, logging.DEBUG)
    """
    logger = logging.getLogger("mineru")

    # Check if handler already exists
    for handler in logger.handlers:
        if isinstance(handler, ConsolePanelHandler):
            # Update existing handler
            handler.console_panel = console_panel
            handler.setLevel(level)
            return

    # Create and add new handler
    handler = ConsolePanelHandler(console_panel)
    handler.setLevel(level)
    logger.addHandler(handler)

    logger.info("Console panel handler connected to logging system")
