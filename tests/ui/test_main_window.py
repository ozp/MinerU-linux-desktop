"""
UI tests for MainWindow.

Tests UI components and interactions using pytest-qt.
Note: These are basic UI tests. Full UI testing would require
a display server and more complex setup.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from mineru_desktop.models.batch import ProcessingOptions, ModelVersion, Language


@pytest.mark.ui
class TestMainWindowBasics:
    """Basic tests for MainWindow initialization and setup."""

    @patch('mineru_desktop.ui.main_window.ConfigManager')
    @patch('mineru_desktop.ui.main_window.MineruClient')
    def test_main_window_imports(self, mock_client, mock_config):
        """Test that MainWindow can be imported without errors."""
        try:
            from mineru_desktop.ui.main_window import MainWindow
            assert MainWindow is not None
        except ImportError as e:
            pytest.fail(f"Failed to import MainWindow: {e}")

    @patch('mineru_desktop.ui.main_window.ConfigManager')
    @patch('mineru_desktop.ui.main_window.MineruClient')
    def test_drag_drop_list_widget_import(self, mock_client, mock_config):
        """Test that DragDropListWidget can be imported."""
        try:
            from mineru_desktop.ui.main_window import DragDropListWidget
            assert DragDropListWidget is not None
        except ImportError as e:
            pytest.fail(f"Failed to import DragDropListWidget: {e}")


@pytest.mark.ui
class TestSettingsDialog:
    """Tests for SettingsDialog component."""

    @patch('mineru_desktop.ui.settings_dialog.keyring')
    def test_settings_dialog_import(self, mock_keyring):
        """Test that SettingsDialog can be imported."""
        try:
            from mineru_desktop.ui.settings_dialog import SettingsDialog
            assert SettingsDialog is not None
        except ImportError as e:
            pytest.fail(f"Failed to import SettingsDialog: {e}")


@pytest.mark.ui
class TestToastNotification:
    """Tests for ToastNotification component."""

    def test_toast_notification_import(self):
        """Test that ToastNotification can be imported."""
        try:
            from mineru_desktop.ui.toast_notification import ToastNotification, ToastType
            assert ToastNotification is not None
            assert ToastType is not None
        except ImportError as e:
            pytest.fail(f"Failed to import ToastNotification: {e}")

    def test_toast_type_enum(self):
        """Test ToastType enum values."""
        from mineru_desktop.ui.toast_notification import ToastType

        # Verify enum has expected values
        assert hasattr(ToastType, 'SUCCESS')
        assert hasattr(ToastType, 'ERROR')
        assert hasattr(ToastType, 'INFO')
        assert hasattr(ToastType, 'WARNING')


@pytest.mark.ui
class TestProcessingOptions:
    """Tests for ProcessingOptions model used in UI."""

    def test_processing_options_defaults(self):
        """Test ProcessingOptions default values."""
        options = ProcessingOptions()

        assert options.is_ocr == True
        assert options.enable_formula == False
        assert options.enable_table == True
        assert options.language == Language.PORTUGUESE
        assert options.model_version == ModelVersion.PIPELINE

    def test_processing_options_custom_values(self):
        """Test ProcessingOptions with custom values."""
        options = ProcessingOptions(
            is_ocr=False,
            enable_formula=True,
            enable_table=False,
            language=Language.ENGLISH,
            model_version=ModelVersion.VLM
        )

        assert options.is_ocr == False
        assert options.enable_formula == True
        assert options.enable_table == False
        assert options.language == Language.ENGLISH
        assert options.model_version == ModelVersion.VLM

    def test_processing_options_to_dict(self):
        """Test converting ProcessingOptions to dictionary."""
        options = ProcessingOptions(
            is_ocr=True,
            enable_formula=False,
            enable_table=True,
            language=Language.PORTUGUESE,
            model_version=ModelVersion.PIPELINE
        )

        options_dict = options.to_dict()

        assert "enable_formula" in options_dict
        assert "enable_table" in options_dict
        assert "model_version" in options_dict
        assert "language" in options_dict

        assert options_dict["enable_formula"] == False
        assert options_dict["enable_table"] == True
        assert options_dict["model_version"] == "pipeline"
        assert options_dict["language"] == "pt"

    def test_processing_options_vlm_excludes_language(self):
        """Test that VLM model excludes language from dict."""
        options = ProcessingOptions(
            is_ocr=True,
            enable_formula=False,
            enable_table=True,
            model_version=ModelVersion.VLM
        )

        options_dict = options.to_dict()

        assert "language" not in options_dict
        assert options_dict["model_version"] == "vlm"


@pytest.mark.ui
class TestModelEnums:
    """Tests for model enums used in UI."""

    def test_model_version_enum(self):
        """Test ModelVersion enum."""
        assert ModelVersion.PIPELINE.value == "pipeline"
        assert ModelVersion.VLM.value == "vlm"

    def test_language_enum(self):
        """Test Language enum."""
        assert Language.CHINESE.value == "ch"
        assert Language.ENGLISH.value == "en"
        assert Language.PORTUGUESE.value == "pt"

    def test_model_version_from_string(self):
        """Test creating ModelVersion from string."""
        assert ModelVersion("pipeline") == ModelVersion.PIPELINE
        assert ModelVersion("vlm") == ModelVersion.VLM

    def test_language_from_string(self):
        """Test creating Language from string."""
        assert Language("ch") == Language.CHINESE
        assert Language("en") == Language.ENGLISH
        assert Language("pt") == Language.PORTUGUESE


@pytest.mark.ui
class TestUIComponentsIntegration:
    """Integration tests for UI components."""

    def test_version_import(self):
        """Test that version can be imported for UI display."""
        try:
            from version import VERSION
            assert VERSION is not None
            assert isinstance(VERSION, str)
            assert len(VERSION) > 0
        except ImportError as e:
            pytest.fail(f"Failed to import VERSION: {e}")

    @patch('mineru_desktop.ui.main_window.ConfigManager')
    def test_config_manager_used_by_ui(self, mock_config_class):
        """Test that UI properly uses ConfigManager."""
        mock_config = Mock()
        mock_config.load_api_token.return_value = "test_token"
        mock_config.load_processing_options.return_value = ProcessingOptions()
        mock_config.load_output_directory.return_value = "/tmp/output"
        mock_config.get_theme_preference.return_value = "light"
        mock_config_class.return_value = mock_config

        # Verify ConfigManager can be instantiated
        from mineru_desktop.core.config import ConfigManager
        config = ConfigManager()
        assert config is not None

    def test_batch_service_import(self):
        """Test that BatchService can be imported for UI use."""
        try:
            from mineru_desktop.services.batch_service import BatchService
            assert BatchService is not None
        except ImportError as e:
            pytest.fail(f"Failed to import BatchService: {e}")

    def test_upload_worker_import(self):
        """Test that UploadWorker can be imported for UI use."""
        try:
            from mineru_desktop.workers.upload_worker import UploadWorker
            assert UploadWorker is not None
        except ImportError as e:
            pytest.fail(f"Failed to import UploadWorker: {e}")


@pytest.mark.ui
class TestFileStateDisplay:
    """Tests for file state display in UI."""

    def test_file_state_display_strings(self, sample_file_status):
        """Test file state display strings."""
        from mineru_desktop.models.batch import FileState

        # Test each state
        sample_file_status.state = FileState.READY
        assert "Pronto" in sample_file_status.get_display_status()

        sample_file_status.state = FileState.UPLOADING
        assert "Enviando" in sample_file_status.get_display_status()

        sample_file_status.state = FileState.PROCESSING
        assert "Processando" in sample_file_status.get_display_status()

        sample_file_status.state = FileState.COMPLETED
        assert "Concluído" in sample_file_status.get_display_status()

        sample_file_status.state = FileState.FAILED
        sample_file_status.error_message = "Test error"
        status = sample_file_status.get_display_status()
        assert "Falha" in status or "Test error" in status


@pytest.mark.ui
@pytest.mark.slow
class TestUIWorkflows:
    """Tests for complete UI workflows (marked as slow)."""

    def test_batch_creation_workflow(self):
        """Test batch creation workflow."""
        from mineru_desktop.models.batch import Batch

        batch = Batch()
        assert batch.batch_id is None
        assert len(batch.files) == 0

        # Add files
        batch.add_file("/path/to/file1.pdf")
        batch.add_file("/path/to/file2.pdf")

        assert len(batch.files) == 2
        assert batch.files[0].filename == "file1.pdf"
        assert batch.files[1].filename == "file2.pdf"

    def test_batch_status_tracking(self):
        """Test batch status tracking."""
        from mineru_desktop.models.batch import Batch, FileState

        batch = Batch()
        batch.add_file("/path/to/file1.pdf")
        batch.add_file("/path/to/file2.pdf")
        batch.add_file("/path/to/file3.pdf")

        # Initially not completed
        assert not batch.all_files_completed()

        # Mark some as completed
        batch.files[0].state = FileState.COMPLETED
        batch.files[1].state = FileState.PROCESSING
        batch.files[2].state = FileState.FAILED

        # Still not all completed
        assert not batch.all_files_completed()

        # Mark remaining as completed
        batch.files[1].state = FileState.COMPLETED

        # Now check counts
        assert batch.get_success_count() == 2
        assert batch.get_failed_count() == 1
