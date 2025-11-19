"""
Unit tests for MineruClient class.

Tests all MineruClient methods including authentication, upload, status check,
and download operations with comprehensive mocking of HTTP requests.
"""

import pytest
import requests
from unittest.mock import Mock, patch, mock_open, MagicMock
from io import BytesIO

from mineru_desktop.core.client import MineruClient
from mineru_desktop.models.batch import ProcessingOptions, ModelVersion, Language


@pytest.mark.unit
class TestMineruClient:
    """Test suite for MineruClient."""

    def test_init_without_token(self):
        """Test client initialization without API token."""
        client = MineruClient()
        assert client.api_token is None

    def test_init_with_token(self, sample_api_token):
        """Test client initialization with API token."""
        client = MineruClient(api_token=sample_api_token)
        assert client.api_token == sample_api_token

    def test_set_api_token(self, mock_client, sample_api_token):
        """Test setting API token."""
        new_token = "new_token_67890"
        mock_client.set_api_token(new_token)
        assert mock_client.api_token == new_token

    def test_get_headers_success(self, mock_client, sample_api_token):
        """Test getting headers with valid token."""
        headers = mock_client.get_headers()
        assert headers == {"Authorization": f"Bearer {sample_api_token}"}

    def test_get_headers_no_token(self):
        """Test getting headers without token raises ValueError."""
        client = MineruClient()
        with pytest.raises(ValueError, match="API token not configured"):
            client.get_headers()

    @patch('mineru_desktop.core.client.requests.post')
    @patch('mineru_desktop.core.client.requests.put')
    def test_upload_batch_success(
        self,
        mock_put,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options,
        mock_batch_response
    ):
        """Test successful batch upload."""
        # Mock POST response for getting upload URLs
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = mock_batch_response
        mock_post.return_value = mock_post_response

        # Mock PUT responses for file uploads
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put.return_value = mock_put_response

        result = mock_client.upload_batch(sample_files, sample_processing_options)

        assert result["batch_id"] == "batch_123"
        assert len(result["uploads"]) == 3
        assert all(upload["status"] == "success" for upload in result["uploads"])
        assert mock_post.call_count == 1
        assert mock_put.call_count == 3

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_no_files(self, mock_post, mock_client, sample_processing_options):
        """Test upload batch with empty file list raises ValueError."""
        with pytest.raises(ValueError, match="No files provided"):
            mock_client.upload_batch([], sample_processing_options)

        mock_post.assert_not_called()

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_connection_error(
        self,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options
    ):
        """Test upload batch with connection error."""
        mock_post.side_effect = requests.ConnectionError("Network error")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            mock_client.upload_batch(sample_files, sample_processing_options)

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_timeout(
        self,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options
    ):
        """Test upload batch with timeout error."""
        mock_post.side_effect = requests.Timeout("Timeout")

        with pytest.raises(TimeoutError, match="timed out"):
            mock_client.upload_batch(sample_files, sample_processing_options)

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_401_error(
        self,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options
    ):
        """Test upload batch with 401 authentication error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Invalid API token"):
            mock_client.upload_batch(sample_files, sample_processing_options)

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_403_error(
        self,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options
    ):
        """Test upload batch with 403 forbidden error."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="Access forbidden"):
            mock_client.upload_batch(sample_files, sample_processing_options)

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_invalid_response(
        self,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options
    ):
        """Test upload batch with invalid API response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": {}}  # Missing batch_id and file_urls
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="missing batch_id or file_urls"):
            mock_client.upload_batch(sample_files, sample_processing_options)

    @patch('mineru_desktop.core.client.requests.post')
    def test_upload_batch_url_count_mismatch(
        self,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options
    ):
        """Test upload batch with URL count mismatch."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "batch_id": "batch_123",
                "file_urls": ["url1"]  # Only 1 URL for 3 files
            }
        }
        mock_post.return_value = mock_response

        with pytest.raises(ValueError, match="URL count mismatch"):
            mock_client.upload_batch(sample_files, sample_processing_options)

    @patch('mineru_desktop.core.client.requests.post')
    @patch('mineru_desktop.core.client.requests.put')
    def test_upload_batch_partial_failure(
        self,
        mock_put,
        mock_post,
        mock_client,
        sample_files,
        sample_processing_options,
        mock_batch_response
    ):
        """Test batch upload with some files failing."""
        mock_post_response = Mock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = mock_batch_response
        mock_post.return_value = mock_post_response

        # Make second upload fail
        def put_side_effect(*args, **kwargs):
            if mock_put.call_count == 2:
                raise requests.HTTPError("Upload failed")
            response = Mock()
            response.status_code = 200
            return response

        mock_put.side_effect = put_side_effect

        result = mock_client.upload_batch(sample_files, sample_processing_options)

        assert result["batch_id"] == "batch_123"
        assert len(result["uploads"]) == 3
        success_count = sum(1 for u in result["uploads"] if u["status"] == "success")
        failed_count = sum(1 for u in result["uploads"] if u["status"] == "failed")
        assert success_count == 2
        assert failed_count == 1

    def test_upload_batch_with_progress_callback(
        self,
        mock_client,
        sample_files,
        sample_processing_options,
        mock_batch_response
    ):
        """Test upload batch with progress callback."""
        progress_values = []

        def progress_callback(progress):
            progress_values.append(progress)

        with patch('mineru_desktop.core.client.requests.post') as mock_post, \
             patch('mineru_desktop.core.client.requests.put') as mock_put:

            mock_post_response = Mock()
            mock_post_response.status_code = 200
            mock_post_response.json.return_value = mock_batch_response
            mock_post.return_value = mock_post_response

            mock_put_response = Mock()
            mock_put_response.status_code = 200
            mock_put.return_value = mock_put_response

            mock_client.upload_batch(
                sample_files,
                sample_processing_options,
                progress_callback=progress_callback
            )

        assert len(progress_values) == 3
        assert progress_values[-1] == 100

    @patch('mineru_desktop.core.client.requests.get')
    def test_get_batch_status_success(
        self,
        mock_get,
        mock_client,
        mock_status_response
    ):
        """Test successful batch status check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_status_response
        mock_get.return_value = mock_response

        result = mock_client.get_batch_status("batch_123")

        assert result == mock_status_response
        mock_get.assert_called_once()

    @patch('mineru_desktop.core.client.requests.get')
    def test_get_batch_status_connection_error(self, mock_get, mock_client):
        """Test batch status check with connection error."""
        mock_get.side_effect = requests.ConnectionError("Network error")

        with pytest.raises(ConnectionError, match="Failed to connect"):
            mock_client.get_batch_status("batch_123")

    @patch('mineru_desktop.core.client.requests.get')
    def test_get_batch_status_timeout(self, mock_get, mock_client):
        """Test batch status check with timeout."""
        mock_get.side_effect = requests.Timeout("Timeout")

        with pytest.raises(TimeoutError, match="timed out"):
            mock_client.get_batch_status("batch_123")

    @patch('mineru_desktop.core.client.requests.get')
    def test_get_batch_status_404_error(self, mock_get, mock_client):
        """Test batch status check with 404 not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response

        with pytest.raises(ValueError, match="Batch ID .* not found"):
            mock_client.get_batch_status("batch_123")

    @patch('mineru_desktop.core.client.requests.get')
    def test_download_result_success(self, mock_get, mock_client, temp_dir):
        """Test successful result download."""
        output_path = f"{temp_dir}/result.zip"
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.iter_content = lambda chunk_size: [b"chunk1", b"chunk2"]
        mock_get.return_value = mock_response

        with patch('builtins.open', mock_open()) as mock_file:
            result = mock_client.download_result(
                "https://example.com/result.zip",
                output_path
            )

        assert result == output_path
        mock_get.assert_called_once()

    @patch('mineru_desktop.core.client.requests.get')
    def test_download_result_connection_error(self, mock_get, mock_client):
        """Test download with connection error."""
        mock_get.side_effect = requests.ConnectionError("Network error")

        with pytest.raises(ConnectionError, match="Failed to download"):
            mock_client.download_result(
                "https://example.com/result.zip",
                "/tmp/result.zip"
            )

    @patch('mineru_desktop.core.client.requests.get')
    def test_download_result_timeout(self, mock_get, mock_client):
        """Test download with timeout."""
        mock_get.side_effect = requests.Timeout("Timeout")

        with pytest.raises(TimeoutError, match="Download timed out"):
            mock_client.download_result(
                "https://example.com/result.zip",
                "/tmp/result.zip"
            )

    def test_client_constants(self):
        """Test that client constants are properly defined."""
        assert MineruClient.API_BASE_URL == "https://mineru.net/api/v4"
        assert MineruClient.MAX_CONCURRENT_UPLOADS == 5
        assert MineruClient.REQUEST_TIMEOUT == 30
        assert MineruClient.UPLOAD_TIMEOUT == 300

    def test_processing_options_dict_conversion(self, sample_processing_options):
        """Test ProcessingOptions to_dict conversion."""
        options_dict = sample_processing_options.to_dict()

        assert options_dict["enable_formula"] == False
        assert options_dict["enable_table"] == True
        assert options_dict["model_version"] == "pipeline"
        assert options_dict["language"] == "pt"

    def test_processing_options_vlm_no_language(self):
        """Test ProcessingOptions with VLM model doesn't include language."""
        options = ProcessingOptions(
            is_ocr=True,
            enable_formula=False,
            enable_table=True,
            model_version=ModelVersion.VLM
        )
        options_dict = options.to_dict()

        assert "language" not in options_dict
        assert options_dict["model_version"] == "vlm"
