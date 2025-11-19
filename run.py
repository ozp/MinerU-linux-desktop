#!/usr/bin/env python3
"""
MinerU Desktop Client - Application Entry Point.

This is the main entry point for the refactored MinerU Desktop Client.
Initializes logging and starts the Qt application.
"""

import sys
import logging
from pathlib import Path

from PySide6.QtWidgets import QApplication

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from mineru_desktop.ui.main_window import MainWindow
from mineru_desktop.utils.logging_config import setup_logging
from version import VERSION


def main():
    """Application entry point."""
    # Setup logging
    log_dir = Path.home() / ".local" / "share" / "MinerU"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "mineru_desktop.log"

    setup_logging(
        level=logging.INFO,
        log_file=str(log_file)
    )

    logger = logging.getLogger(__name__)
    logger.info(f"=" * 60)
    logger.info(f"MinerU Desktop Client v{VERSION} starting...")
    logger.info(f"=" * 60)

    # Create Qt application
    app = QApplication(sys.argv)
    app.setApplicationName("MinerU Desktop Client")
    app.setOrganizationName("MinerU")
    app.setApplicationVersion(VERSION)

    # Create and show main window
    window = MainWindow()
    window.show()

    logger.info("Application window displayed")

    # Run application
    exit_code = app.exec()

    logger.info(f"Application exiting with code: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
