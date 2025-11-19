"""MinerU Linux Desktop Client - Main Entry Point.

A desktop application for interacting with the MinerU API on Linux systems.
This application provides a graphical user interface for uploading documents,
monitoring processing status, and downloading processed results.

This version follows SOLID principles and modern Python best practices,
with proper separation of concerns, comprehensive logging, type hints,
and modular architecture.

The main components include:
    - MainWindow: Primary application window (src/ui/main_window.py)
    - MineruAPIClient: API client for backend communication (src/services/api_client.py)
    - BatchService: Batch processing orchestration (src/services/batch_service.py)
    - SettingsDialog: Configuration interface (src/ui/settings_dialog.py)

Typical usage example:
    $ python main.py

The application will launch the GUI where users can:
    1. Configure API settings (File > Settings)
    2. Add files for processing
    3. Start batch processing
    4. Monitor progress and download results

Architecture:
    The application follows a modular architecture with clear separation:
    - UI Layer: PySide6-based interface components (src/ui/)
    - Services Layer: API client and batch processing logic (src/services/)
    - Configuration: Centralized config and constants (src/config/)
    - Models: Data structures for batches and options (src/models/)
    - Workers: Async operations for upload and polling (src/workers/)
    - Utilities: Logging configuration and helpers (src/utils/)

Security:
    - API tokens stored securely using Linux Keyring
    - HTTPS-only communication with MinerU API
    - No sensitive data logged or printed
    - Input validation at all entry points

For detailed documentation, see:
    - docs/API.md - API reference
    - docs/ARCHITECTURE.md - Architecture overview
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
