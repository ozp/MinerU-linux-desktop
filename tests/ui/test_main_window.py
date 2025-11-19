"""UI tests for MainWindow using QTest."""
import os
import pytest
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from main import MainWindow, UploadWorker
from mineru_client import MineruClient


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.mark.ui
class TestMainWindowUI:
    """Tests for MainWindow UI components."""

    def test_window_initialization(self, qapp, mock_keyring):
        """Test main window initializes correctly."""
        window = MainWindow()
        assert window.windowTitle().startswith("MinerU Desktop Client")
        assert window.selected_files == []
        assert window.current_batch_id is None

    def test_ui_components_exist(self, qapp, mock_keyring):
        """Test that all UI components are present."""
        window = MainWindow()
        assert window.add_files_button is not None
        assert window.file_list is not None
        assert window.process_button is not None
        assert window.progress_bar is not None
        assert window.open_folder_button is not None

    def test_process_button_disabled_initially(self, qapp, mock_keyring):
        """Test process button is disabled when no files are selected."""
        window = MainWindow()
        assert window.process_button.isEnabled() is False

    def test_progress_bar_hidden_initially(self, qapp, mock_keyring):
        """Test progress bar is hidden initially."""
        window = MainWindow()
        assert window.progress_bar.isVisible() is False

    def test_open_folder_button_disabled_initially(self, qapp, mock_keyring):
        """Test open folder button is disabled initially."""
        window = MainWindow()
        assert window.open_folder_button.isEnabled() is False


@pytest.mark.ui
class TestFileSelection:
    """Tests for file selection functionality."""

    def test_add_files_enables_process_button(self, qapp, mock_keyring, sample_pdf_file, monkeypatch):
        """Test that adding files enables the process button."""
        window = MainWindow()

        # Mock file dialog to return our sample file
        def mock_exec(self):
            return True

        def mock_selected_files(self):
            return [sample_pdf_file]

        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.exec", mock_exec)
        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.selectedFiles", mock_selected_files)

        # Trigger add files
        window.add_files()

        assert len(window.selected_files) == 1
        assert window.process_button.isEnabled() is True
        assert window.file_list.count() == 1

    def test_remove_files_disables_process_button(self, qapp, mock_keyring, sample_pdf_file, monkeypatch):
        """Test that removing all files disables the process button."""
        window = MainWindow()

        # Add a file first
        def mock_exec(self):
            return True

        def mock_selected_files(self):
            return [sample_pdf_file]

        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.exec", mock_exec)
        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.selectedFiles", mock_selected_files)

        window.add_files()
        assert window.process_button.isEnabled() is True

        # Remove the file
        window.file_list.selectAll()
        window.remove_selected_files()

        assert len(window.selected_files) == 0
        assert window.process_button.isEnabled() is False
        assert window.file_list.count() == 0

    def test_duplicate_files_not_added(self, qapp, mock_keyring, sample_pdf_file, monkeypatch):
        """Test that duplicate files are not added to the list."""
        window = MainWindow()

        def mock_exec(self):
            return True

        def mock_selected_files(self):
            return [sample_pdf_file]

        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.exec", mock_exec)
        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.selectedFiles", mock_selected_files)

        # Add file twice
        window.add_files()
        window.add_files()

        # Should only have one file
        assert len(window.selected_files) == 1
        assert window.file_list.count() == 1


@pytest.mark.ui
class TestUploadWorker:
    """Tests for UploadWorker thread."""

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    def test_upload_worker_emits_progress(self, mock_put, mock_post, qapp, mock_keyring, sample_files):
        """Test that upload worker emits progress signals."""
        # Mock API responses
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_123",
                "file_urls": [
                    "https://s3.example.com/upload1",
                    "https://s3.example.com/upload2",
                    "https://s3.example.com/upload3"
                ]
            }
        }
        mock_post.return_value.status_code = 200
        mock_put.return_value.status_code = 200

        client = MineruClient()
        worker = UploadWorker(client, sample_files)

        progress_values = []

        def on_progress(value):
            progress_values.append(value)

        worker.progress_updated.connect(on_progress)

        # Run worker
        worker.run()

        # Wait for signals
        QTest.qWait(100)

        assert len(progress_values) > 0
        assert max(progress_values) == 100

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    def test_upload_worker_emits_completion(self, mock_put, mock_post, qapp, mock_keyring, sample_files):
        """Test that upload worker emits completion signal."""
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_123",
                "file_urls": [
                    "https://s3.example.com/upload1",
                    "https://s3.example.com/upload2",
                    "https://s3.example.com/upload3"
                ]
            }
        }
        mock_post.return_value.status_code = 200
        mock_put.return_value.status_code = 200

        client = MineruClient()
        worker = UploadWorker(client, sample_files)

        completed = []

        def on_completed(result):
            completed.append(result)

        worker.upload_completed.connect(on_completed)

        # Run worker
        worker.run()

        # Wait for signals
        QTest.qWait(100)

        assert len(completed) == 1
        assert completed[0]["batch_id"] == "batch_123"

    def test_upload_worker_emits_failure(self, qapp, mock_keyring, sample_files):
        """Test that upload worker emits failure signal on error."""
        client = MineruClient()
        client.api_token = None  # Force authentication error

        worker = UploadWorker(client, sample_files)

        failed = []

        def on_failed(error):
            failed.append(error)

        worker.upload_failed.connect(on_failed)

        # Run worker
        worker.run()

        # Wait for signals
        QTest.qWait(100)

        assert len(failed) == 1
        assert "not configured" in failed[0]


@pytest.mark.ui
class TestProcessing:
    """Tests for file processing workflow."""

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    def test_start_processing_creates_worker(self, mock_put, mock_post, qapp, mock_keyring, sample_pdf_file, monkeypatch):
        """Test that start_processing creates upload worker."""
        window = MainWindow()

        # Add a file
        def mock_exec(self):
            return True

        def mock_selected_files(self):
            return [sample_pdf_file]

        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.exec", mock_exec)
        monkeypatch.setattr("PySide6.QtWidgets.QFileDialog.selectedFiles", mock_selected_files)

        window.add_files()

        # Mock API responses
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_123",
                "file_urls": ["https://s3.example.com/upload1"]
            }
        }
        mock_post.return_value.status_code = 200
        mock_put.return_value.status_code = 200

        # Start processing
        window.start_processing()

        assert window.upload_worker is not None
        assert window.progress_bar.isVisible() is True
        assert window.process_button.isEnabled() is False
        assert window.add_files_button.isEnabled() is False

    def test_start_processing_without_files_shows_warning(self, qapp, mock_keyring, monkeypatch):
        """Test that start_processing shows warning when no files selected."""
        window = MainWindow()

        warning_shown = []

        def mock_warning(*args):
            warning_shown.append(args)

        monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.warning", mock_warning)

        window.start_processing()

        assert len(warning_shown) > 0


@pytest.mark.ui
class TestFileStatusUpdates:
    """Tests for file status updates."""

    def test_update_file_status(self, qapp, mock_keyring, sample_pdf_file):
        """Test updating file status in the list."""
        window = MainWindow()

        # Manually add a file to the list
        from PySide6.QtWidgets import QListWidgetItem
        filename = os.path.basename(sample_pdf_file)
        item = QListWidgetItem(f"[Pronto] {filename}")
        item.setData(Qt.UserRole, sample_pdf_file)
        window.file_list.addItem(item)
        window.file_status_map[filename] = "ready"

        # Update status
        window.update_file_status(filename, "Concluído")

        # Verify update
        updated_item = window.file_list.item(0)
        assert "[Concluído]" in updated_item.text()
        assert filename in updated_item.text()


@pytest.mark.ui
class TestMenuActions:
    """Tests for menu actions."""

    def test_settings_menu_opens_dialog(self, qapp, mock_keyring, monkeypatch):
        """Test that settings menu opens settings dialog."""
        window = MainWindow()

        dialog_opened = []

        def mock_exec(self):
            dialog_opened.append(True)
            return False

        monkeypatch.setattr("settings_dialog.SettingsDialog.exec", mock_exec)

        window.open_settings()

        assert len(dialog_opened) > 0

    def test_about_menu_shows_dialog(self, qapp, mock_keyring, monkeypatch):
        """Test that about menu shows about dialog."""
        window = MainWindow()

        about_shown = []

        def mock_about(*args):
            about_shown.append(args)

        monkeypatch.setattr("PySide6.QtWidgets.QMessageBox.about", mock_about)

        window.show_about()

        assert len(about_shown) > 0
