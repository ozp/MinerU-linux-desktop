"""
Settings Dialog for MinerU Desktop Client.

Provides a configuration interface for API token (using keyring)
and processing options. Now uses centralized ConfigManager.
"""

import os
from typing import Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QGroupBox, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt

from ..config.config_manager import get_config
from ..config.constants import ModelVersion, Language
from ..models.processing_options import ProcessingOptions
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """Dialog for configuring MinerU API settings."""

    def __init__(self, parent: Optional[QDialog] = None) -> None:
        """
        Initialize the settings dialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.config = get_config()
        self.setup_ui()
        self.load_settings()
        logger.debug("Settings dialog initialized")

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Settings")
        self.setMinimumWidth(550)

        # Main layout
        layout = QVBoxLayout()

        # API Token Section
        layout.addWidget(self._create_token_section())

        # Output Directory Section
        layout.addWidget(self._create_output_section())

        # Processing Options Section
        layout.addWidget(self._create_options_section())

        # Buttons
        layout.addLayout(self._create_button_row())

        self.setLayout(layout)

    def _create_token_section(self) -> QGroupBox:
        """
        Create the API token configuration section.

        Returns:
            QGroupBox with token input widgets
        """
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

        return token_group

    def _create_output_section(self) -> QGroupBox:
        """
        Create the output directory configuration section.

        Returns:
            QGroupBox with output directory widgets
        """
        output_group = QGroupBox("Output Settings")
        output_layout = QVBoxLayout()

        output_label = QLabel("Output Directory:")
        output_row = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Select output directory for downloads")

        self.select_folder_button = QPushButton("Selecionar...")
        self.select_folder_button.clicked.connect(self._select_output_folder)

        output_row.addWidget(self.output_path_input)
        output_row.addWidget(self.select_folder_button)

        output_layout.addWidget(output_label)
        output_layout.addLayout(output_row)
        output_group.setLayout(output_layout)

        return output_group

    def _create_options_section(self) -> QGroupBox:
        """
        Create the processing options configuration section.

        Returns:
            QGroupBox with processing option widgets
        """
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
        self.model_combo.addItem("Pipeline (Legado - Melhor para Português)", ModelVersion.PIPELINE.value)
        self.model_combo.addItem("VLM (Novo - Sem suporte a idioma)", ModelVersion.VLM.value)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        options_layout.addLayout(model_layout)

        # Language Selection
        language_layout = QHBoxLayout()
        self.language_label = QLabel("Select OCR Language:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Chinese", Language.CHINESE.value)
        self.language_combo.addItem("English", Language.ENGLISH.value)
        self.language_combo.addItem("Portuguese", Language.PORTUGUESE.value)

        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        options_layout.addLayout(language_layout)

        # Language help text
        self.language_help = QLabel("Nota: Configuração de idioma apenas disponível para modelo Pipeline")
        self.language_help.setStyleSheet("color: #FF6B6B; font-size: 10px; font-style: italic;")
        self.language_help.setWordWrap(True)
        options_layout.addWidget(self.language_help)

        options_group.setLayout(options_layout)
        return options_group

    def _create_button_row(self) -> QHBoxLayout:
        """
        Create the dialog button row.

        Returns:
            QHBoxLayout with Save and Cancel buttons
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self._save_settings)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)

        return button_layout

    def _select_output_folder(self) -> None:
        """Open file dialog to select output directory."""
        current_dir = self.output_path_input.text() or os.path.expanduser("~/Documents")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            current_dir
        )
        if folder:
            self.output_path_input.setText(folder)
            logger.debug(f"Output directory selected: {folder}")

    def _on_model_changed(self) -> None:
        """Handle model selection change to enable/disable language settings."""
        model_value = self.model_combo.currentData()
        is_pipeline = model_value == ModelVersion.PIPELINE.value

        self.language_label.setEnabled(is_pipeline)
        self.language_combo.setEnabled(is_pipeline)

        if not is_pipeline:
            self.language_help.setStyleSheet(
                "color: #FF6B6B; font-size: 10px; font-style: italic; font-weight: bold;"
            )
        else:
            self.language_help.setStyleSheet(
                "color: #FF6B6B; font-size: 10px; font-style: italic;"
            )

    def load_settings(self) -> None:
        """Load settings from ConfigManager."""
        try:
            # Load token
            if self.config.api_token:
                self.token_input.setText(self.config.api_token)

            # Load output directory
            self.output_path_input.setText(self.config.output_directory)

            # Load processing options
            options = self.config.processing_options

            self.force_ocr_checkbox.setChecked(options.is_ocr)
            self.enable_formula_checkbox.setChecked(options.enable_formula)
            self.enable_table_checkbox.setChecked(options.enable_table)

            # Set model version
            model_index = self.model_combo.findData(options.model_version.value)
            if model_index >= 0:
                self.model_combo.setCurrentIndex(model_index)

            # Set language
            language_index = self.language_combo.findData(options.language.value)
            if language_index >= 0:
                self.language_combo.setCurrentIndex(language_index)

            # Update UI based on model selection
            self._on_model_changed()

            logger.debug("Settings loaded successfully")

        except Exception as e:
            logger.error(f"Error loading settings: {e}", exc_info=True)

    def _save_settings(self) -> None:
        """Save settings to ConfigManager."""
        try:
            # Validate and save token
            token = self.token_input.text().strip()
            if not token:
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

            # Update configuration
            self.config.api_token = token
            self.config.output_directory = output_dir

            # Create new processing options
            model_value = self.model_combo.currentData()
            language_value = self.language_combo.currentData()

            processing_options = ProcessingOptions(
                is_ocr=self.force_ocr_checkbox.isChecked(),
                enable_formula=self.enable_formula_checkbox.isChecked(),
                enable_table=self.enable_table_checkbox.isChecked(),
                model_version=ModelVersion(model_value),
                language=Language(language_value),
            )

            self.config.processing_options = processing_options

            # Save to file
            self.config.save()

            logger.info("Settings saved successfully")

            QMessageBox.information(
                self,
                "Success",
                "Settings saved successfully!"
            )
            self.accept()

        except Exception as e:
            logger.error(f"Error saving settings: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save settings: {str(e)}"
            )
