"""
Settings Dialog for MinerU Desktop Client

Provides a configuration interface for API token and processing options.
"""

import configparser
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QGroupBox, QMessageBox
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """Dialog for configuring MinerU API settings."""

    CONFIG_FILE = "config.ini"

    def __init__(self, parent=None):
        """Initialize the settings dialog."""
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(500)

        # Main layout
        layout = QVBoxLayout()

        # API Token Section
        token_group = QGroupBox("API Configuration")
        token_layout = QVBoxLayout()

        token_label = QLabel("MinerU API Token:")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your MinerU API token")
        self.token_input.setEchoMode(QLineEdit.Password)

        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        token_group.setLayout(token_layout)

        # Processing Options Section
        options_group = QGroupBox("Processing Options")
        options_layout = QVBoxLayout()

        # Checkboxes
        self.force_ocr_checkbox = QCheckBox("Force OCR")
        self.force_ocr_checkbox.setToolTip("Enable Optical Character Recognition for all documents")

        self.enable_formula_checkbox = QCheckBox("Enable Formula Recognition")
        self.enable_formula_checkbox.setToolTip("Detect and process mathematical formulas")

        self.enable_table_checkbox = QCheckBox("Enable Table Recognition")
        self.enable_table_checkbox.setToolTip("Detect and process tables in documents")

        options_layout.addWidget(self.force_ocr_checkbox)
        options_layout.addWidget(self.enable_formula_checkbox)
        options_layout.addWidget(self.enable_table_checkbox)

        # Language Selection
        language_layout = QHBoxLayout()
        language_label = QLabel("Select OCR Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Chinese", "ch")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Portuguese", "pt")

        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combo)

        options_layout.addLayout(language_layout)
        options_group.setLayout(options_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)

        # Add all sections to main layout
        layout.addWidget(token_group)
        layout.addWidget(options_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def load_settings(self):
        """Load settings from config file."""
        if not os.path.exists(self.CONFIG_FILE):
            return

        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE)

        if "API" in config:
            self.token_input.setText(config["API"].get("token", ""))

        if "Processing" in config:
            self.force_ocr_checkbox.setChecked(
                config["Processing"].getboolean("is_ocr", False)
            )
            self.enable_formula_checkbox.setChecked(
                config["Processing"].getboolean("enable_formula", False)
            )
            self.enable_table_checkbox.setChecked(
                config["Processing"].getboolean("enable_table", False)
            )

            language = config["Processing"].get("language", "en")
            index = self.language_combo.findData(language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

    def save_settings(self):
        """Save settings to config file."""
        config = configparser.ConfigParser()

        # API Section
        config["API"] = {
            "token": self.token_input.text().strip()
        }

        # Processing Section
        config["Processing"] = {
            "is_ocr": str(self.force_ocr_checkbox.isChecked()),
            "enable_formula": str(self.enable_formula_checkbox.isChecked()),
            "enable_table": str(self.enable_table_checkbox.isChecked()),
            "language": self.language_combo.currentData()
        }

        # Write to file
        try:
            with open(self.CONFIG_FILE, "w") as configfile:
                config.write(configfile)

            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully!"
            )
            self.accept()

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )
