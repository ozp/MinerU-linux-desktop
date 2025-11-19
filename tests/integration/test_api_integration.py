"""Integration tests for MinerU API."""
import os
import pytest
from unittest.mock import patch, Mock
from mineru_client import MineruClient
from exceptions import AuthenticationError, APIError, NetworkError


@pytest.mark.integration
class TestAPIWorkflow:
    """Tests for complete API workflow."""

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    @patch('mineru_client.requests.get')
    def test_complete_upload_to_download_workflow(
        self, mock_get, mock_put, mock_post, mock_keyring, sample_files, temp_dir
    ):
        """Test complete workflow from upload to download."""
        # Step 1: Mock upload batch (POST + PUT)
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_workflow_123",
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
        client.output_directory = temp_dir

        # Upload files
        upload_result = client.upload_batch(sample_files)
        assert upload_result["batch_id"] == "batch_workflow_123"
        assert all(u["status"] == "success" for u in upload_result["uploads"])

        # Step 2: Mock get batch status (GET) - processing
        mock_get.return_value.json.return_value = {
            "data": {
                "extract_result": [
                    {"file_name": "document_0.pdf", "state": "processing"},
                    {"file_name": "document_1.pdf", "state": "processing"},
                    {"file_name": "document_2.pdf", "state": "processing"}
                ]
            }
        }
        mock_get.return_value.status_code = 200

        status_result = client.get_batch_status("batch_workflow_123")
        assert len(status_result["data"]["extract_result"]) == 3
        assert all(f["state"] == "processing" for f in status_result["data"]["extract_result"])

        # Step 3: Mock get batch status (GET) - done
        mock_get.return_value.json.return_value = {
            "data": {
                "extract_result": [
                    {
                        "file_name": "document_0.pdf",
                        "state": "done",
                        "full_zip_url": "https://s3.example.com/result1.zip"
                    },
                    {
                        "file_name": "document_1.pdf",
                        "state": "done",
                        "full_zip_url": "https://s3.example.com/result2.zip"
                    },
                    {
                        "file_name": "document_2.pdf",
                        "state": "done",
                        "full_zip_url": "https://s3.example.com/result3.zip"
                    }
                ]
            }
        }

        status_result = client.get_batch_status("batch_workflow_123")
        assert all(f["state"] == "done" for f in status_result["data"]["extract_result"])

        # Step 4: Mock download (GET with streaming)
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'fake zip content']
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        download_path = client.download_result(
            "https://s3.example.com/result1.zip",
            "document_0_result.zip"
        )

        assert os.path.exists(download_path)
        assert download_path.endswith("document_0_result.zip")

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    @patch('mineru_client.requests.get')
    def test_workflow_with_failed_file(
        self, mock_get, mock_put, mock_post, mock_keyring, sample_files, temp_dir
    ):
        """Test workflow when one file fails processing."""
        # Upload batch
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_fail_123",
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
        client.output_directory = temp_dir

        upload_result = client.upload_batch(sample_files)
        assert upload_result["batch_id"] == "batch_fail_123"

        # Get status with one failed file
        mock_get.return_value.json.return_value = {
            "data": {
                "extract_result": [
                    {
                        "file_name": "document_0.pdf",
                        "state": "done",
                        "full_zip_url": "https://s3.example.com/result1.zip"
                    },
                    {
                        "file_name": "document_1.pdf",
                        "state": "failed",
                        "err_msg": "Processing error: Invalid format"
                    },
                    {
                        "file_name": "document_2.pdf",
                        "state": "done",
                        "full_zip_url": "https://s3.example.com/result3.zip"
                    }
                ]
            }
        }
        mock_get.return_value.status_code = 200

        status_result = client.get_batch_status("batch_fail_123")
        results = status_result["data"]["extract_result"]

        done_count = sum(1 for r in results if r["state"] == "done")
        failed_count = sum(1 for r in results if r["state"] == "failed")

        assert done_count == 2
        assert failed_count == 1
        assert results[1]["err_msg"] == "Processing error: Invalid format"


@pytest.mark.integration
class TestAPIErrorHandling:
    """Tests for API error handling in integration scenarios."""

    @patch('mineru_client.requests.post')
    def test_upload_with_invalid_token(self, mock_post, mock_keyring, sample_files):
        """Test upload with invalid authentication token."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        client = MineruClient()

        with pytest.raises(AuthenticationError, match="Invalid API token"):
            client.upload_batch(sample_files)

    @patch('mineru_client.requests.post')
    def test_upload_with_forbidden_access(self, mock_post, mock_keyring, sample_files):
        """Test upload with forbidden access."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.HTTPError("403 Forbidden")
        mock_post.return_value = mock_response

        client = MineruClient()

        with pytest.raises(AuthenticationError, match="Access forbidden"):
            client.upload_batch(sample_files)

    @patch('mineru_client.requests.post')
    def test_upload_with_server_error(self, mock_post, mock_keyring, sample_files):
        """Test upload with server error."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_response.raise_for_status.side_effect = requests.HTTPError("500 Internal Server Error")
        mock_post.return_value = mock_response

        client = MineruClient()

        with pytest.raises(APIError) as exc_info:
            client.upload_batch(sample_files)

        assert exc_info.value.status_code == 500

    @patch('mineru_client.requests.get')
    def test_status_check_batch_not_found(self, mock_get, mock_keyring):
        """Test status check for non-existent batch."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Batch not found"
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = MineruClient()

        with pytest.raises(APIError, match="not found") as exc_info:
            client.get_batch_status("nonexistent_batch")

        assert exc_info.value.status_code == 404


@pytest.mark.integration
class TestAPIRetryBehavior:
    """Tests for API retry and resilience."""

    @patch('mineru_client.requests.post')
    def test_upload_eventually_succeeds_after_retry(self, mock_post, mock_keyring, sample_files):
        """Test that upload can succeed after initial failures."""
        # First call fails, second succeeds
        call_count = [0]

        def side_effect(*args, **kwargs):
            call_count[0] += 1
            if call_count[0] == 1:
                raise Exception("Connection failed")
            else:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "data": {
                        "batch_id": "batch_retry_123",
                        "file_urls": [
                            "https://s3.example.com/upload1",
                            "https://s3.example.com/upload2",
                            "https://s3.example.com/upload3"
                        ]
                    }
                }
                mock_response.status_code = 200
                return mock_response

        mock_post.side_effect = side_effect

        client = MineruClient()

        # First attempt should fail
        with pytest.raises(Exception):
            client.upload_batch(sample_files)

        # Second attempt should succeed
        result = client.upload_batch(sample_files)
        assert result["batch_id"] == "batch_retry_123"


@pytest.mark.integration
class TestMultipleFileFormats:
    """Tests for handling multiple file formats."""

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    def test_upload_mixed_file_formats(self, mock_put, mock_post, mock_keyring, temp_dir):
        """Test uploading files with different formats."""
        # Create files with different formats
        pdf_file = os.path.join(temp_dir, "document.pdf")
        docx_file = os.path.join(temp_dir, "document.docx")
        png_file = os.path.join(temp_dir, "image.png")

        for file_path in [pdf_file, docx_file, png_file]:
            with open(file_path, 'wb') as f:
                f.write(b'test content')

        files = [pdf_file, docx_file, png_file]

        # Mock API responses
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_mixed_123",
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
        result = client.upload_batch(files)

        assert result["batch_id"] == "batch_mixed_123"
        assert len(result["uploads"]) == 3
