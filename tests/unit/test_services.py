"""
Unit tests for service modules.

Tests UploadService and DownloadService with mocked client operations.
"""

import os
import pytest
from unittest.mock import Mock, patch, MagicMock

from mineru_desktop.services.upload_service import UploadService
from mineru_desktop.services.download_service import DownloadService
from mineru_desktop.models.batch import Batch, FileStatus, FileState, ProcessingOptions
from mineru_desktop.core.client import MineruClient


@pytest.mark.unit
class TestUploadService:
    """Test suite for UploadService."""

    def test_init(self, mock_client):
        """Test UploadService initialization."""
        service = UploadService(mock_client)
        assert service.client == mock_client

    def test_upload_batch_no_files(self, mock_client):
        """Test upload batch with no files raises ValueError."""
        service = UploadService(mock_client)
        batch = Batch()  # Empty batch

        with pytest.raises(ValueError, match="No files in batch"):
            service.upload_batch(batch)

    def test_upload_batch_success(self, mock_client, sample_batch, sample_files):
        """Test successful batch upload."""
        # Add files to batch
        for file_path in sample_files:
            sample_batch.add_file(file_path)

        # Mock client response
        mock_client.upload_batch = Mock(return_value={
            "batch_id": "batch_456",
            "uploads": [
                {"file": "test_0.pdf", "status": "success"},
                {"file": "test_1.pdf", "status": "success"},
                {"file": "test_2.pdf", "status": "success"}
            ]
        })

        service = UploadService(mock_client)
        service.upload_batch(sample_batch)

        # Verify batch ID was set
        assert sample_batch.batch_id == "batch_456"

        # Verify all files are in PROCESSING state
        for file_status in sample_batch.files:
            assert file_status.state == FileState.PROCESSING

        mock_client.upload_batch.assert_called_once()

    def test_upload_batch_partial_failure(self, mock_client, sample_batch, sample_files):
        """Test batch upload with some files failing."""
        # Add files to batch
        for file_path in sample_files:
            sample_batch.add_file(file_path)

        # Mock client response with one failure
        mock_client.upload_batch = Mock(return_value={
            "batch_id": "batch_789",
            "uploads": [
                {"file": "test_0.pdf", "status": "success"},
                {"file": "test_1.pdf", "status": "failed", "error": "Upload error"},
                {"file": "test_2.pdf", "status": "success"}
            ]
        })

        service = UploadService(mock_client)
        service.upload_batch(sample_batch)

        # Verify batch ID was set
        assert sample_batch.batch_id == "batch_789"

        # Verify file statuses
        assert sample_batch.files[0].state == FileState.PROCESSING
        assert sample_batch.files[1].state == FileState.FAILED
        assert sample_batch.files[1].error_message == "Upload error"
        assert sample_batch.files[2].state == FileState.PROCESSING

    def test_upload_batch_complete_failure(self, mock_client, sample_batch, sample_files):
        """Test batch upload with complete failure."""
        # Add files to batch
        for file_path in sample_files:
            sample_batch.add_file(file_path)

        # Mock client to raise exception
        mock_client.upload_batch = Mock(side_effect=Exception("Network error"))

        service = UploadService(mock_client)

        with pytest.raises(Exception, match="Network error"):
            service.upload_batch(sample_batch)

        # Verify all files are marked as failed
        for file_status in sample_batch.files:
            assert file_status.state == FileState.FAILED
            assert file_status.error_message == "Network error"

    def test_upload_batch_with_progress_callback(
        self,
        mock_client,
        sample_batch,
        sample_files
    ):
        """Test batch upload with progress callback."""
        # Add files to batch
        for file_path in sample_files:
            sample_batch.add_file(file_path)

        progress_values = []

        def progress_callback(progress):
            progress_values.append(progress)

        # Mock client response
        mock_client.upload_batch = Mock(return_value={
            "batch_id": "batch_999",
            "uploads": [
                {"file": "test_0.pdf", "status": "success"},
                {"file": "test_1.pdf", "status": "success"},
                {"file": "test_2.pdf", "status": "success"}
            ]
        })

        service = UploadService(mock_client)
        service.upload_batch(sample_batch, progress_callback=progress_callback)

        # Verify client upload was called
        mock_client.upload_batch.assert_called_once()

    def test_upload_batch_sets_uploading_state(self, mock_client, sample_batch, sample_files):
        """Test that files are set to UPLOADING state before upload."""
        # Add files to batch
        for file_path in sample_files:
            sample_batch.add_file(file_path)

        # Mock client to check state during upload
        def mock_upload(*args, **kwargs):
            # At this point, all files should be in UPLOADING state
            for file_status in sample_batch.files:
                assert file_status.state == FileState.UPLOADING
            return {
                "batch_id": "batch_111",
                "uploads": [
                    {"file": "test_0.pdf", "status": "success"},
                    {"file": "test_1.pdf", "status": "success"},
                    {"file": "test_2.pdf", "status": "success"}
                ]
            }

        mock_client.upload_batch = Mock(side_effect=mock_upload)

        service = UploadService(mock_client)
        service.upload_batch(sample_batch)


@pytest.mark.unit
class TestDownloadService:
    """Test suite for DownloadService."""

    def test_init(self, mock_client, temp_dir):
        """Test DownloadService initialization."""
        service = DownloadService(mock_client, temp_dir)
        assert service.client == mock_client
        assert service.output_directory == temp_dir

    def test_download_file_success(self, mock_client, temp_dir):
        """Test successful file download."""
        # Mock client download
        output_path = os.path.join(temp_dir, "result.zip")
        mock_client.download_result = Mock(return_value=output_path)

        service = DownloadService(mock_client, temp_dir)
        result = service.download_file(
            "https://example.com/result.zip",
            "result.zip"
        )

        assert result == output_path
        mock_client.download_result.assert_called_once()

    def test_download_file_creates_directory(self, mock_client, temp_dir):
        """Test that download creates output directory if missing."""
        new_dir = os.path.join(temp_dir, "new_output")
        output_path = os.path.join(new_dir, "result.zip")

        mock_client.download_result = Mock(return_value=output_path)

        service = DownloadService(mock_client, new_dir)

        # Directory should be created during download
        with patch('os.makedirs') as mock_makedirs:
            service.download_file(
                "https://example.com/result.zip",
                "result.zip"
            )
            mock_makedirs.assert_called_once_with(new_dir, exist_ok=True)

    def test_download_file_failure(self, mock_client, temp_dir):
        """Test file download with failure."""
        mock_client.download_result = Mock(side_effect=Exception("Download failed"))

        service = DownloadService(mock_client, temp_dir)

        with pytest.raises(Exception, match="Download failed"):
            service.download_file(
                "https://example.com/result.zip",
                "result.zip"
            )

    def test_set_output_directory(self, mock_client, temp_dir):
        """Test updating output directory."""
        service = DownloadService(mock_client, "/old/path")
        assert service.output_directory == "/old/path"

        service.set_output_directory(temp_dir)
        assert service.output_directory == temp_dir

    def test_download_constructs_correct_path(self, mock_client, temp_dir):
        """Test that download constructs correct output path."""
        mock_client.download_result = Mock(return_value="/path/to/file.zip")

        service = DownloadService(mock_client, temp_dir)
        service.download_file("https://example.com/result.zip", "result.zip")

        # Verify correct path was passed to client
        expected_path = os.path.join(temp_dir, "result.zip")
        mock_client.download_result.assert_called_once_with(
            "https://example.com/result.zip",
            expected_path
        )


@pytest.mark.unit
class TestBatchModel:
    """Test suite for Batch model methods."""

    def test_add_file(self, sample_batch):
        """Test adding a file to batch."""
        file_status = sample_batch.add_file("/path/to/test.pdf")

        assert file_status.filename == "test.pdf"
        assert file_status.file_path == "/path/to/test.pdf"
        assert file_status.state == FileState.READY
        assert file_status in sample_batch.files

    def test_get_file_by_name_found(self, sample_batch):
        """Test finding a file by name."""
        sample_batch.add_file("/path/to/test.pdf")
        sample_batch.add_file("/path/to/other.pdf")

        file_status = sample_batch.get_file_by_name("test.pdf")

        assert file_status is not None
        assert file_status.filename == "test.pdf"

    def test_get_file_by_name_not_found(self, sample_batch):
        """Test finding a file that doesn't exist."""
        sample_batch.add_file("/path/to/test.pdf")

        file_status = sample_batch.get_file_by_name("nonexistent.pdf")

        assert file_status is None

    def test_all_files_completed_empty_batch(self):
        """Test all_files_completed on empty batch."""
        batch = Batch()
        assert batch.all_files_completed() == False

    def test_all_files_completed_true(self, sample_batch):
        """Test all_files_completed when all files are done."""
        file1 = sample_batch.add_file("/path/to/file1.pdf")
        file2 = sample_batch.add_file("/path/to/file2.pdf")

        file1.state = FileState.COMPLETED
        file2.state = FileState.COMPLETED

        assert sample_batch.all_files_completed() == True

    def test_all_files_completed_false(self, sample_batch):
        """Test all_files_completed when some files are still processing."""
        file1 = sample_batch.add_file("/path/to/file1.pdf")
        file2 = sample_batch.add_file("/path/to/file2.pdf")

        file1.state = FileState.COMPLETED
        file2.state = FileState.PROCESSING

        assert sample_batch.all_files_completed() == False

    def test_get_success_count(self, sample_batch):
        """Test counting successfully completed files."""
        file1 = sample_batch.add_file("/path/to/file1.pdf")
        file2 = sample_batch.add_file("/path/to/file2.pdf")
        file3 = sample_batch.add_file("/path/to/file3.pdf")

        file1.state = FileState.COMPLETED
        file2.state = FileState.FAILED
        file3.state = FileState.COMPLETED

        assert sample_batch.get_success_count() == 2

    def test_get_failed_count(self, sample_batch):
        """Test counting failed files."""
        file1 = sample_batch.add_file("/path/to/file1.pdf")
        file2 = sample_batch.add_file("/path/to/file2.pdf")
        file3 = sample_batch.add_file("/path/to/file3.pdf")

        file1.state = FileState.COMPLETED
        file2.state = FileState.FAILED
        file3.state = FileState.DOWNLOAD_FAILED

        assert sample_batch.get_failed_count() == 2

    def test_get_processing_count(self, sample_batch):
        """Test counting files still processing."""
        file1 = sample_batch.add_file("/path/to/file1.pdf")
        file2 = sample_batch.add_file("/path/to/file2.pdf")
        file3 = sample_batch.add_file("/path/to/file3.pdf")
        file4 = sample_batch.add_file("/path/to/file4.pdf")

        file1.state = FileState.COMPLETED
        file2.state = FileState.PROCESSING
        file3.state = FileState.UPLOADING
        file4.state = FileState.FAILED

        assert sample_batch.get_processing_count() == 2


@pytest.mark.unit
class TestFileStatus:
    """Test suite for FileStatus model."""

    def test_is_final_state_completed(self, sample_file_status):
        """Test is_final_state for COMPLETED."""
        sample_file_status.state = FileState.COMPLETED
        assert sample_file_status.is_final_state() == True

    def test_is_final_state_failed(self, sample_file_status):
        """Test is_final_state for FAILED."""
        sample_file_status.state = FileState.FAILED
        assert sample_file_status.is_final_state() == True

    def test_is_final_state_download_failed(self, sample_file_status):
        """Test is_final_state for DOWNLOAD_FAILED."""
        sample_file_status.state = FileState.DOWNLOAD_FAILED
        assert sample_file_status.is_final_state() == True

    def test_is_final_state_processing(self, sample_file_status):
        """Test is_final_state for PROCESSING."""
        sample_file_status.state = FileState.PROCESSING
        assert sample_file_status.is_final_state() == False

    def test_get_display_status_ready(self, sample_file_status):
        """Test display status for READY state."""
        sample_file_status.state = FileState.READY
        assert sample_file_status.get_display_status() == "Pronto"

    def test_get_display_status_uploading(self, sample_file_status):
        """Test display status for UPLOADING state."""
        sample_file_status.state = FileState.UPLOADING
        assert sample_file_status.get_display_status() == "Enviando..."

    def test_get_display_status_processing(self, sample_file_status):
        """Test display status for PROCESSING state."""
        sample_file_status.state = FileState.PROCESSING
        assert sample_file_status.get_display_status() == "Processando no servidor..."

    def test_get_display_status_completed(self, sample_file_status):
        """Test display status for COMPLETED state."""
        sample_file_status.state = FileState.COMPLETED
        assert sample_file_status.get_display_status() == "Concluído"

    def test_get_display_status_failed(self, sample_file_status):
        """Test display status for FAILED state."""
        sample_file_status.state = FileState.FAILED
        sample_file_status.error_message = "Network error"
        status = sample_file_status.get_display_status()
        assert "Falha" in status
        assert "Network error" in status
