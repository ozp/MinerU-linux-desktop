"""Unit tests for MineruClient class."""
import os
import tempfile
import configparser
import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from mineru_client import MineruClient
from exceptions import (
    AuthenticationError, ValidationError, APIError,
    NetworkError, UploadError, DownloadError
)


@pytest.mark.unit
class TestMineruClientInit:
    """Tests for MineruClient initialization."""

    def test_init_defaults(self, mock_keyring):
        """Test client initialization with default values."""
        client = MineruClient()
        assert client.is_ocr is True
        assert client.enable_formula is False
        assert client.enable_table is True
        assert client.language == "pt"
        assert client.model_version == "pipeline"

    def test_init_loads_token_from_keyring(self, mock_keyring):
        """Test that initialization loads token from keyring."""
        client = MineruClient()
        mock_keyring["get"].assert_called_once_with("MinerU", "api_token")
        assert client.api_token == "test_token_12345"


@pytest.mark.unit
class TestMineruClientLoadConfig:
    """Tests for load_config method."""

    def test_load_config_from_file(self, temp_dir, mock_keyring, monkeypatch):
        """Test loading configuration from config file."""
        # Create a config file
        config_path = os.path.join(temp_dir, "config.ini")
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "False",
            "enable_formula": "True",
            "enable_table": "False",
            "language": "en",
            "model_version": "vlm"
        }
        config["Paths"] = {
            "output_directory": temp_dir
        }
        with open(config_path, "w") as f:
            config.write(f)

        # Change working directory to temp_dir
        monkeypatch.chdir(temp_dir)

        client = MineruClient()
        assert client.is_ocr is False
        assert client.enable_formula is True
        assert client.enable_table is False
        assert client.language == "en"
        assert client.model_version == "vlm"
        assert client.output_directory == temp_dir

    def test_load_config_invalid_language_uses_default(self, temp_dir, mock_keyring, monkeypatch, capsys):
        """Test that invalid language code falls back to default."""
        config_path = os.path.join(temp_dir, "config.ini")
        config = configparser.ConfigParser()
        config["Settings"] = {
            "language": "invalid_lang"
        }
        with open(config_path, "w") as f:
            config.write(f)

        monkeypatch.chdir(temp_dir)
        client = MineruClient()
        assert client.language == "pt"  # Default
        captured = capsys.readouterr()
        assert "Invalid language code" in captured.out

    def test_load_config_invalid_model_uses_default(self, temp_dir, mock_keyring, monkeypatch, capsys):
        """Test that invalid model version falls back to default."""
        config_path = os.path.join(temp_dir, "config.ini")
        config = configparser.ConfigParser()
        config["Settings"] = {
            "model_version": "invalid_model"
        }
        with open(config_path, "w") as f:
            config.write(f)

        monkeypatch.chdir(temp_dir)
        client = MineruClient()
        assert client.model_version == "pipeline"  # Default
        captured = capsys.readouterr()
        assert "Invalid model version" in captured.out


@pytest.mark.unit
class TestMineruClientGetHeaders:
    """Tests for get_headers method."""

    def test_get_headers_with_token(self, mock_keyring):
        """Test getting headers with valid token."""
        client = MineruClient()
        headers = client.get_headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_12345"

    def test_get_headers_without_token(self, monkeypatch):
        """Test getting headers without token raises error."""
        monkeypatch.setattr("keyring.get_password", Mock(return_value=None))
        client = MineruClient()
        with pytest.raises(AuthenticationError, match="not configured"):
            client.get_headers()


@pytest.mark.unit
class TestMineruClientGetProcessingOptions:
    """Tests for get_processing_options method."""

    def test_processing_options_pipeline_model(self, mock_keyring):
        """Test processing options for pipeline model includes language."""
        client = MineruClient()
        client.model_version = "pipeline"
        client.language = "pt"
        options = client.get_processing_options()
        assert options["enable_formula"] is False
        assert options["enable_table"] is True
        assert options["model_version"] == "pipeline"
        assert options["language"] == "pt"

    def test_processing_options_vlm_model(self, mock_keyring):
        """Test processing options for VLM model excludes language."""
        client = MineruClient()
        client.model_version = "vlm"
        options = client.get_processing_options()
        assert options["model_version"] == "vlm"
        assert "language" not in options


@pytest.mark.unit
class TestMineruClientUploadBatch:
    """Tests for upload_batch method."""

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    def test_upload_batch_success(self, mock_put, mock_post, mock_keyring, sample_files):
        """Test successful batch upload."""
        # Mock POST response (get upload URLs)
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

        # Mock PUT response (file uploads)
        mock_put.return_value.status_code = 200

        client = MineruClient()
        result = client.upload_batch(sample_files)

        assert result["batch_id"] == "batch_123"
        assert len(result["uploads"]) == 3
        assert all(u["status"] == "success" for u in result["uploads"])

        # Verify POST was called
        mock_post.assert_called_once()
        # Verify PUT was called for each file
        assert mock_put.call_count == 3

    def test_upload_batch_no_files(self, mock_keyring):
        """Test upload with no files raises error."""
        client = MineruClient()
        with pytest.raises(ValidationError, match="No files provided"):
            client.upload_batch([])

    def test_upload_batch_invalid_file(self, mock_keyring):
        """Test upload with non-existent file raises error."""
        client = MineruClient()
        with pytest.raises(ValidationError, match="Invalid file"):
            client.upload_batch(["/nonexistent/file.pdf"])

    @patch('mineru_client.requests.post')
    def test_upload_batch_network_error(self, mock_post, mock_keyring, sample_files):
        """Test upload with network error."""
        mock_post.side_effect = Exception("Connection failed")

        client = MineruClient()
        with pytest.raises(Exception):
            client.upload_batch(sample_files)

    @patch('mineru_client.requests.post')
    def test_upload_batch_auth_error(self, mock_post, mock_keyring, sample_files):
        """Test upload with authentication error."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.raise_for_status.side_effect = requests.HTTPError("401 Unauthorized")
        mock_post.return_value = mock_response

        client = MineruClient()
        with pytest.raises(AuthenticationError):
            client.upload_batch(sample_files)

    @patch('mineru_client.requests.post')
    def test_upload_batch_api_error(self, mock_post, mock_keyring, sample_files):
        """Test upload with invalid API response."""
        mock_post.return_value.json.return_value = {
            "data": {}  # Missing batch_id and file_urls
        }
        mock_post.return_value.status_code = 200

        client = MineruClient()
        with pytest.raises(APIError, match="missing batch_id"):
            client.upload_batch(sample_files)

    @patch('mineru_client.requests.post')
    def test_upload_batch_url_count_mismatch(self, mock_post, mock_keyring, sample_files):
        """Test upload with URL count mismatch."""
        mock_post.return_value.json.return_value = {
            "data": {
                "batch_id": "batch_123",
                "file_urls": ["https://s3.example.com/upload1"]  # Only 1 URL for 3 files
            }
        }
        mock_post.return_value.status_code = 200

        client = MineruClient()
        with pytest.raises(APIError, match="URL count mismatch"):
            client.upload_batch(sample_files)

    @patch('mineru_client.requests.post')
    @patch('mineru_client.requests.put')
    def test_upload_batch_with_progress_callback(self, mock_put, mock_post, mock_keyring, sample_files):
        """Test upload with progress callback."""
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

        progress_values = []

        def progress_callback(progress):
            progress_values.append(progress)

        client = MineruClient()
        result = client.upload_batch(sample_files, progress_callback=progress_callback)

        assert len(progress_values) > 0
        assert max(progress_values) == 100


@pytest.mark.unit
class TestMineruClientGetBatchStatus:
    """Tests for get_batch_status method."""

    @patch('mineru_client.requests.get')
    def test_get_batch_status_success(self, mock_get, mock_keyring):
        """Test successful batch status retrieval."""
        mock_get.return_value.json.return_value = {
            "data": {
                "extract_result": [
                    {"file_name": "test.pdf", "state": "done"}
                ]
            }
        }
        mock_get.return_value.status_code = 200

        client = MineruClient()
        result = client.get_batch_status("batch_123")

        assert "data" in result
        assert "extract_result" in result["data"]

    def test_get_batch_status_invalid_batch_id(self, mock_keyring):
        """Test batch status with invalid batch ID."""
        client = MineruClient()
        with pytest.raises(ValidationError):
            client.get_batch_status("")

    @patch('mineru_client.requests.get')
    def test_get_batch_status_not_found(self, mock_get, mock_keyring):
        """Test batch status with non-existent batch."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        client = MineruClient()
        with pytest.raises(APIError, match="not found"):
            client.get_batch_status("batch_999")


@pytest.mark.unit
class TestMineruClientDownloadResult:
    """Tests for download_result method."""

    @patch('mineru_client.requests.get')
    def test_download_result_success(self, mock_get, mock_keyring, temp_dir):
        """Test successful file download."""
        # Mock streaming response
        mock_response = Mock()
        mock_response.iter_content.return_value = [b'chunk1', b'chunk2']
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        client = MineruClient()
        client.output_directory = temp_dir

        result_path = client.download_result("https://example.com/file.zip", "result.zip")

        assert os.path.exists(result_path)
        assert result_path.endswith("result.zip")

    def test_download_result_invalid_url(self, mock_keyring):
        """Test download with invalid URL."""
        client = MineruClient()
        with pytest.raises(ValidationError, match="URL must be"):
            client.download_result("", "result.zip")

    def test_download_result_invalid_filename(self, mock_keyring):
        """Test download with invalid filename."""
        client = MineruClient()
        with pytest.raises(ValidationError, match="Filename must be"):
            client.download_result("https://example.com/file.zip", "")

    @patch('mineru_client.requests.get')
    def test_download_result_network_error(self, mock_get, mock_keyring, temp_dir):
        """Test download with network error."""
        mock_get.side_effect = Exception("Network error")

        client = MineruClient()
        client.output_directory = temp_dir

        with pytest.raises(DownloadError):
            client.download_result("https://example.com/file.zip", "result.zip")
