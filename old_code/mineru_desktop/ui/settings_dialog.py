"""
Settings Dialog for MinerU Desktop Client.

Provides configuration interface for API token and processing options.
"""

import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QComboBox, QPushButton, QGroupBox, QMessageBox,
    QFileDialog
)
from PySide6.QtCore import Qt

from mineru_desktop.core.config import ConfigManager
from mineru_desktop.models.batch import ProcessingOptions, ModelVersion, Language
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """Dialog for configuring MinerU API settings."""

    def __init__(self, parent=None, config_manager: ConfigManager = None):
        """
        Initialize the settings dialog.

        Args:
            parent: Parent widget
            config_manager: Configuration manager instance
        """
        super().__init__(parent)
        self.config_manager = config_manager or ConfigManager()
        logger.debug("SettingsDialog initialized")

        self.setup_ui()
        self.load_settings()

    def setup_ui(self) -> None:
        """Set up the user interface."""
        self.setWindowTitle("Configurações")
        self.setMinimumWidth(600)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(16)

        # API Token Section
        token_group = self._create_api_token_group()
        layout.addWidget(token_group)

        # Output Directory Section
        output_group = self._create_output_directory_group()
        layout.addWidget(output_group)

        # Processing Options Section
        options_group = self._create_processing_options_group()
        layout.addWidget(options_group)

        # Buttons
        button_layout = self._create_button_layout()
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _create_api_token_group(self) -> QGroupBox:
        """Create API token configuration group."""
        token_group = QGroupBox("Configuração da API")
        token_layout = QVBoxLayout()

        token_label = QLabel("Token da API MinerU:")
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Cole seu token da API aqui")
        self.token_input.setEchoMode(QLineEdit.Password)

        # Show/hide token button
        show_token_btn = QPushButton("👁️")
        show_token_btn.setMaximumWidth(40)
        show_token_btn.setCheckable(True)
        show_token_btn.toggled.connect(self._toggle_token_visibility)

        token_row = QHBoxLayout()
        token_row.addWidget(self.token_input)
        token_row.addWidget(show_token_btn)

        token_help = QLabel(
            "ℹ️ Token armazenado com segurança no sistema de keyring do Linux"
        )
        token_help.setStyleSheet("color: gray; font-size: 11px;")
        token_help.setWordWrap(True)

        token_layout.addWidget(token_label)
        token_layout.addLayout(token_row)
        token_layout.addWidget(token_help)
        token_group.setLayout(token_layout)

        return token_group

    def _create_output_directory_group(self) -> QGroupBox:
        """Create output directory configuration group."""
        output_group = QGroupBox("Configurações de Saída")
        output_layout = QVBoxLayout()

        output_label = QLabel("Pasta de Saída:")
        output_row = QHBoxLayout()
        self.output_path_input = QLineEdit()
        self.output_path_input.setPlaceholderText("Selecione a pasta para downloads")

        self.select_folder_button = QPushButton("📁 Selecionar...")
        self.select_folder_button.setObjectName("secondaryButton")
        self.select_folder_button.clicked.connect(self.select_output_folder)

        output_row.addWidget(self.output_path_input)
        output_row.addWidget(self.select_folder_button)

        output_layout.addWidget(output_label)
        output_layout.addLayout(output_row)
        output_group.setLayout(output_layout)

        return output_group

    def _create_processing_options_group(self) -> QGroupBox:
        """Create processing options configuration group."""
        options_group = QGroupBox("Opções de Processamento")
        options_layout = QVBoxLayout()

        # Checkboxes
        self.force_ocr_checkbox = QCheckBox("Forçar OCR")
        self.force_ocr_checkbox.setToolTip(
            "Habilita Reconhecimento Óptico de Caracteres para todos os documentos"
        )

        self.enable_formula_checkbox = QCheckBox("Reconhecimento de Fórmulas")
        self.enable_formula_checkbox.setToolTip(
            "Detecta e processa fórmulas matemáticas"
        )

        self.enable_table_checkbox = QCheckBox("Reconhecimento de Tabelas")
        self.enable_table_checkbox.setToolTip(
            "Detecta e processa tabelas em documentos"
        )

        options_layout.addWidget(self.force_ocr_checkbox)
        options_layout.addWidget(self.enable_formula_checkbox)
        options_layout.addWidget(self.enable_table_checkbox)

        # Model Version Selection
        model_layout = QHBoxLayout()
        model_label = QLabel("Modelo MinerU:")
        self.model_combo = QComboBox()
        self.model_combo.addItem(
            "Pipeline (Legado - Melhor para Português)",
            ModelVersion.PIPELINE.value
        )
        self.model_combo.addItem(
            "VLM (Novo - Sem suporte a idioma)",
            ModelVersion.VLM.value
        )
        self.model_combo.currentIndexChanged.connect(self.on_model_changed)

        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        options_layout.addLayout(model_layout)

        # Language Selection
        language_layout = QHBoxLayout()
        self.language_label = QLabel("Idioma do OCR:")
        self.language_combo = QComboBox()
        self.language_combo.addItem("Chinês", Language.CHINESE.value)
        self.language_combo.addItem("Inglês", Language.ENGLISH.value)
        self.language_combo.addItem("Português", Language.PORTUGUESE.value)

        language_layout.addWidget(self.language_label)
        language_layout.addWidget(self.language_combo)
        options_layout.addLayout(language_layout)

        # Language help text
        self.language_help = QLabel(
            "⚠️ Configuração de idioma disponível apenas para o modelo Pipeline"
        )
        self.language_help.setStyleSheet("color: #e67e22; font-size: 11px; font-style: italic;")
        self.language_help.setWordWrap(True)
        options_layout.addWidget(self.language_help)

        options_group.setLayout(options_layout)
        return options_group

    def _create_button_layout(self) -> QHBoxLayout:
        """Create dialog button layout."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("💾 Salvar")
        self.save_button.clicked.connect(self.save_settings)

        cancel_button = QPushButton("✖️ Cancelar")
        cancel_button.setObjectName("secondaryButton")
        cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(cancel_button)

        return button_layout

    def _toggle_token_visibility(self, checked: bool) -> None:
        """
        Toggle API token visibility.

        Args:
            checked: Whether to show the token
        """
        if checked:
            self.token_input.setEchoMode(QLineEdit.Normal)
        else:
            self.token_input.setEchoMode(QLineEdit.Password)

    def select_output_folder(self) -> None:
        """Open file dialog to select output directory."""
        current_dir = self.output_path_input.text() or os.path.expanduser("~/Documents")
        folder = QFileDialog.getExistingDirectory(
            self,
            "Selecionar Pasta de Saída",
            current_dir
        )
        if folder:
            self.output_path_input.setText(folder)
            logger.debug(f"Output folder selected: {folder}")

    def on_model_changed(self) -> None:
        """Handle model selection change to enable/disable language settings."""
        is_pipeline = self.model_combo.currentData() == ModelVersion.PIPELINE.value
        self.language_label.setEnabled(is_pipeline)
        self.language_combo.setEnabled(is_pipeline)

        if not is_pipeline:
            self.language_help.setStyleSheet(
                "color: #e74c3c; font-size: 11px; font-style: italic; font-weight: bold;"
            )
        else:
            self.language_help.setStyleSheet(
                "color: #e67e22; font-size: 11px; font-style: italic;"
            )

    def load_settings(self) -> None:
        """Load settings from configuration manager."""
        logger.debug("Loading settings")

        # Load API token
        token = self.config_manager.load_api_token()
        if token:
            self.token_input.setText(token)

        # Load output directory
        output_dir = self.config_manager.load_output_directory()
        self.output_path_input.setText(output_dir)

        # Load processing options
        options = self.config_manager.load_processing_options()
        self.force_ocr_checkbox.setChecked(options.is_ocr)
        self.enable_formula_checkbox.setChecked(options.enable_formula)
        self.enable_table_checkbox.setChecked(options.enable_table)

        # Set model version
        model_index = self.model_combo.findData(options.model_version.value)
        if model_index >= 0:
            self.model_combo.setCurrentIndex(model_index)

        # Set language
        lang_index = self.language_combo.findData(options.language.value)
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)

        # Update UI based on model
        self.on_model_changed()

        logger.debug("Settings loaded successfully")

    def save_settings(self) -> None:
        """Save settings to configuration manager."""
        logger.debug("Saving settings")

        try:
            # Validate and save API token
            token = self.token_input.text().strip()
            if not token:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "O token da API está vazio. Por favor, insira um token válido."
                )
                return

            self.config_manager.save_api_token(token)

            # Validate output directory
            output_dir = self.output_path_input.text().strip()
            if not output_dir:
                QMessageBox.warning(
                    self,
                    "Aviso",
                    "Por favor, selecione uma pasta de saída."
                )
                return

            # Create processing options
            model_value = self.model_combo.currentData()
            lang_value = self.language_combo.currentData()

            processing_options = ProcessingOptions(
                is_ocr=self.force_ocr_checkbox.isChecked(),
                enable_formula=self.enable_formula_checkbox.isChecked(),
                enable_table=self.enable_table_checkbox.isChecked(),
                language=Language(lang_value),
                model_version=ModelVersion(model_value)
            )

            # Save settings
            self.config_manager.save_settings(processing_options, output_dir)

            logger.info("Settings saved successfully")

            QMessageBox.information(
                self,
                "Sucesso",
                "✅ Configurações salvas com sucesso!"
            )
            self.accept()

        except ValueError as e:
            logger.error(f"Validation error: {e}")
            QMessageBox.warning(
                self,
                "Erro de Validação",
                f"Erro ao validar configurações:\n\n{str(e)}"
            )

        except Exception as e:
            logger.error(f"Failed to save settings: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "Erro",
                f"Falha ao salvar configurações:\n\n{str(e)}"
            )
