"""
MinerU Linux Desktop Client

A desktop application for interacting with the MinerU API on Linux systems.
This app allows users to upload documents, monitor processing status,
and download processed results.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtCore import Qt


class MainWindow(QMainWindow):
    """Main application window for MinerU Desktop Client."""

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("MinerU Desktop Client")
        self.setMinimumSize(800, 600)


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
