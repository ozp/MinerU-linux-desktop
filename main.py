"""
MinerU Linux Desktop Client

A desktop application for interacting with the MinerU API on Linux systems.
This app allows users to upload documents, monitor processing status,
and download processed results.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from settings_dialog import SettingsDialog


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

        # Create menu bar
        self.create_menu_bar()

        # Set central widget (placeholder for now)
        central_label = QLabel("Welcome to MinerU Desktop Client")
        central_label.setAlignment(Qt.AlignCenter)
        self.setCentralWidget(central_label)

    def create_menu_bar(self):
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        # Settings action
        settings_action = QAction("&Settings", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self.open_settings)
        file_menu.addAction(settings_action)

        # Exit action
        file_menu.addSeparator()
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_settings(self):
        """Open the settings dialog."""
        dialog = SettingsDialog(self)
        dialog.exec()


def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
