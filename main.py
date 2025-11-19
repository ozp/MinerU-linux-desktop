"""MinerU Linux Desktop Client - Refactored Version.

A desktop application for interacting with the MinerU API on Linux systems.
This application provides a graphical user interface for uploading documents,
monitoring processing status, and downloading processed results.

This version has been refactored following SOLID principles and modern
Python best practices, with proper separation of concerns, logging,
type hints, and modular architecture.

The main components include:
    - MainWindow: Primary application window (src/ui/main_window.py)
    - MineruClient: API client for backend communication (mineru_client.py)
    - SettingsDialog: Configuration interface (settings_dialog.py)

Typical usage example:
    $ python main.py

The application will launch the GUI where users can:
    1. Configure API settings (File > Settings)
    2. Add files for processing
    3. Start batch processing
    4. Monitor progress and download results

Architecture:
    The application follows a modular architecture with clear separation:
    - UI Layer: PySide6-based interface components in src/ui/
    - Business Logic: Processing coordinators in src/core/
    - API Client: HTTP communication layer in mineru_client.py
    - Utilities: Logging, validation, and helpers in src/utils/

Security:
    - API tokens stored securely using Linux Keyring
    - HTTPS-only communication with MinerU API
    - Input validation using dedicated validators module

For detailed API documentation, see docs/API.md
For architecture details, see docs/ARCHITECTURE.md
"""

import sys
from PySide6.QtWidgets import QApplication

from src.ui import MainWindow
from src.utils import setup_logging




def main() -> None:
    """Application entry point.

    This function initializes the logging system, creates the Qt application,
    and starts the main event loop. It serves as the bootstrap for the entire
    application lifecycle.

    The initialization sequence:
        1. Setup logging system (configured for INFO level)
        2. Create Qt application instance
        3. Create and show main window
        4. Start Qt event loop

    Logs are written to:
        ~/.local/share/MinerU/mineru.log

    Exit codes:
        0: Normal termination
        1: Unhandled exception during execution

    Example:
        $ python main.py
        # Application window appears
        # Logs written to ~/.local/share/MinerU/mineru.log

    Note:
        This function does not return until the application is closed.
        The event loop runs indefinitely until sys.exit() is called.
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
