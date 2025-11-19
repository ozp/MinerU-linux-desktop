"""
MinerU Linux Desktop Client - Refactored Version

A desktop application for interacting with the MinerU API on Linux systems.
This app allows users to upload documents, monitor processing status,
and download processed results.

This version has been refactored following SOLID principles and modern
Python best practices, with proper separation of concerns, logging,
type hints, and modular architecture.
"""

import sys
from PySide6.QtWidgets import QApplication

from src.ui import MainWindow
from src.utils import setup_logging




def main() -> None:
    """
    Application entry point.

    This function initializes the logging system, creates the Qt application,
    and starts the main event loop.
    """
    # Setup logging (INFO level by default)
    # Logs will be written to ~/.local/share/MinerU/mineru.log
    setup_logging()

    # Create Qt application
    app = QApplication(sys.argv)

    # Create and show main window
    window = MainWindow()
    window.show()

    # Start event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
