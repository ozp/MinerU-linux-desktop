"""Settings Dialog for MinerU Desktop Client.

Provides a configuration interface for API token (using keyring) and processing options.

This module implements a Qt dialog for configuring:
    - API authentication token (stored securely in system keyring)
    - Output directory for downloaded results
    - Processing options (OCR, formula recognition, table recognition)
    - Model selection (Pipeline vs VLM)
    - Language selection (for Pipeline model only)

Security:
    API tokens are stored using Linux Keyring, never in plaintext files.
    Only non-sensitive settings are saved to config.ini.

Example:
    >>> from settings_dialog import SettingsDialog
    >>> dialog = SettingsDialog(parent_window)
    >>> if dialog.exec() == QDialog.Accepted:
    ...     # Settings were saved, reload client config
    ...     client.load_config()

For detailed documentation, see docs/API.md#settingsdialog
"""

import configparser
import os
import keyring
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QGroupBox, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """Dialog for configuring MinerU API settings.

    Provides a user-friendly interface for configuring all application settings
    including secure API token storage, processing options, and output preferences.

    Attributes:
        CONFIG_FILE (str): Path to config file ("config.ini")
        KEYRING_SERVICE (str): Service name for keyring ("MinerU")
        KEYRING_USERNAME (str): Username for keyring ("api_token")

    UI Components:
        - API Token input (password field)
        - Output directory selector (with browse button)
        - Processing option checkboxes (OCR, formula, table)
        - Model selection dropdown (Pipeline/VLM)
        - Language selection dropdown (Pipeline only)
        - Save/Cancel buttons

    Example:
        >>> dialog = SettingsDialog(main_window)
        >>> result = dialog.exec()
        >>> if result == QDialog.Accepted:
        ...     print("Settings saved successfully")
    """

    CONFIG_FILE = "config.ini"
    KEYRING_SERVICE = "MinerU"
    KEYRING_USERNAME = "api_token"

    def __init__(self, parent=None):
        """Initialize the settings dialog.

        Args:
            parent: Parent widget (typically MainWindow). Optional.

        Side Effects:
            - Creates and sets up all UI components
            - Loads current settings from keyring and config file
        """
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(550)

        # Main layout
        layout = QVBoxLayout()

        # API Token Section
        token_group = QGroupBox("API Configuration")
        token_layout = QVBoxLayout()

        token_label = QLabel("MinerU API Token:")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Enter your MinerU API token")
        self.token_input.setEchoMode(QLineEdit.Password)

        token_help = QLabel("(Token is stored securely using Linux Keyring)")
        token_help.setStyleSheet("color: gray; font-size: 10px;")

        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_input)
        token_layout.addWidget(token_help)
        token_group.setLayout(token_layout)

        # Output Directory Section
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()

        output_label = QLabel("Output Directory:")
        output_row = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output directory for downloads")

        self.select_folder_button = QPushButton("Selecionar...")
        self.select_folder_button.clicked.connect(self.select_output_folder)

        output_row.addWidget(self.output_path_input)
        output_row.addWidget(self.select_folder_button)

        output_layout.addWidget(output_label)
        output_layout.addLayout(output_row)
        output_group.setLayout(output_layout)

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

        # Model Version Selection
        model_layout = QHBoxLayout()
        model_label = QLabel("MinerU Model:")
        self.model_combo = QComboBox()
        self.model_combo.addItem("Pipeline (Legado - Melhor para Português)", "pipeline")
        self.model_combo.addItem("VLM (Novo - Sem suporte a idioma)", "vlm")
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        options_layout.addLayout(model_layout)

        # Language Selection
        language_layout = QHBoxLayout()
        self.language_label = QLabel("Select OCR Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Chinese", "ch")
        self.language_combo.addItem("English", "en")
        self.language_combo.addItem("Portuguese", "pt")

        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)

        options_layout.addLayout(language_layout)

        # Language help text
        self.language_help = QLabel("Nota: Configuração de idioma apenas disponível para modelo Pipeline")
        self.language_help.setStyleSheet("color: #FF6B6B; font-size: 10px; font-style: italic;")
        self.language_help.setWordWrap(True)
        options_layout.addWidget(self.language_help)

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
        layout.addWidget(output_group)
        layout.addWidget(options_group)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def select_output_folder(self):
        """Open file dialog to select output directory."""
        current_dir = self.output_path_input.text() or os.path.expanduser("~/Documents")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir
        )
        if folder:
            self.output_path_input.setText(folder)

    def on_model_changed(self):
        """Handle model selection change to enable/disable language settings."""
        is_pipeline = self.model_combo.currentData() == "pipeline"
        self.language_label.setEnabled(is_pipeline)
        self.language_combo.setEnabled(is_pipeline)

        if not is_pipeline:
            self.language_help.setStyleSheet("color: #FF6B6B; font-size: 10px; font-style: italic; font-weight: bold;")
        else:
            self.language_help.setStyleSheet("color: #FF6B6B; font-size: 10px; font-style: italic;")

    def load_settings(self):
        """Load settings from keyring and config file."""
        # Load token from keyring (secure storage)
        try:
            token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
            if token:
                self.token_input.setText(token)
        except Exception as e:
            print(f"Warning: Could not load token from keyring: {e}")

        # Load non-sensitive settings from config.ini
        if not os.path.exists(self.CONFIG_FILE):
            # Set defaults
            self.output_path_input.setText(os.path.expanduser("~/Documents/MinerU_Output"))
            self.force_ocr_checkbox.setChecked(True)
            self.enable_table_checkbox.setChecked(True)
            # Set Portuguese as default
            index = self.language_combo.findData("pt")
            if index >= 0:
                self.language_combo.setCurrentIndex(index)
            # Set pipeline as default model
            model_index = self.model_combo.findData("pipeline")
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)
            self.on_model_changed()
            return

        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE)

        # Load output directory
        if "Paths" in config:
            output_dir = config["Paths"].get("output_directory", "~/Documents/MinerU_Output")
            self.output_path_input.setText(os.path.expanduser(output_dir))

        # Load processing options
        if "Settings" in config:
            self.force_ocr_checkbox.setChecked(
                config["Settings"].getboolean("is_ocr", True)
            )
            self.enable_formula_checkbox.setChecked(
                config["Settings"].getboolean("enable_formula", False)
            )
            self.enable_table_checkbox.setChecked(
                config["Settings"].getboolean("enable_table", True)
            )

            # Load model version
            model_version = config["Settings"].get("model_version", "pipeline")
            model_index = self.model_combo.findData(model_version)
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)

            # Load language
            language = config["Settings"].get("language", "pt")
            index = self.language_combo.findData(language)
            if index >= 0:
                self.language_combo.setCurrentIndex(index)

            # Update UI based on model selection
            self.on_model_changed()

    def save_settings(self):
        """Save settings to keyring and config file."""
        try:
            # Save token to keyring (secure storage)
            token = self.token_input.text().strip()
            if token:
                keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME, token)
            else:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "API Token is empty. Please enter a valid token."
                )
                return

            # Validate output directory
            output_dir = self.output_path_input.text().strip()
            if not output_dir:
                QMessageBox.warning(
                    self,
                    "Warning",
                    "Please select an output directory."
                )
                return

            # Create output directory if it doesn't exist
            expanded_path = os.path.expanduser(output_dir)
            os.makedirs(expanded_path, exist_ok=True)

            # Save non-sensitive settings to config.ini
            config = configparser.ConfigParser()

            config["Settings"] = {
                "is_ocr": str(self.force_ocr_checkbox.isChecked()),
                "enable_formula": str(self.enable_formula_checkbox.isChecked()),
                "enable_table": str(self.enable_table_checkbox.isChecked()),
                "language": self.language_combo.currentData(),
                "model_version": self.model_combo.currentData()
            }

            config["Paths"] = {
                "output_directory": output_dir
            }

            # Write to file
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
