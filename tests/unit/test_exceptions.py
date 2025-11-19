"""
Unit tests for custom exception classes.

Tests all custom exception types and their attributes.
"""

import pytest

from mineru_desktop.core.exceptions import (
    MineruException,
    ValidationError,
    AuthenticationError,
    APIError,
    NetworkError,
    ConfigurationError,
    FileOperationError,
    UploadError,
    DownloadError,
    BatchProcessingError
)


@pytest.mark.unit
class TestMineruException:
    """Tests for base MineruException."""

    def test_basic_exception(self):
        """Test basic exception creation."""
        exc = MineruException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"
        assert exc.original_exception is None

    def test_exception_with_original(self):
        """Test exception with original exception."""
        original = ValueError("Original error")
        exc = MineruException("Wrapper error", original_exception=original)

        assert exc.message == "Wrapper error"
        assert exc.original_exception == original


@pytest.mark.unit
class TestValidationError:
    """Tests for ValidationError."""

    def test_validation_error(self):
        """Test ValidationError creation."""
        exc = ValidationError("Invalid input")
        assert str(exc) == "Invalid input"
        assert isinstance(exc, MineruException)

    def test_validation_error_with_original(self):
        """Test ValidationError with original exception."""
        original = ValueError("Original error")
        exc = ValidationError("Validation failed", original_exception=original)

        assert exc.message == "Validation failed"
        assert exc.original_exception == original


@pytest.mark.unit
class TestAuthenticationError:
    """Tests for AuthenticationError."""

    def test_authentication_error(self):
        """Test AuthenticationError creation."""
        exc = AuthenticationError("Invalid credentials")
        assert str(exc) == "Invalid credentials"
        assert isinstance(exc, MineruException)


@pytest.mark.unit
class TestAPIError:
    """Tests for APIError."""

    def test_api_error_basic(self):
        """Test basic APIError creation."""
        exc = APIError("API request failed")
        assert str(exc) == "API request failed"
        assert exc.status_code is None
        assert exc.response_data is None

    def test_api_error_with_status(self):
        """Test APIError with status code."""
        exc = APIError("Not found", status_code=404)
        assert exc.status_code == 404

    def test_api_error_with_response_data(self):
        """Test APIError with response data."""
        response_data = {"error": "Not found", "code": "404"}
        exc = APIError("Not found", status_code=404, response_data=response_data)

        assert exc.status_code == 404
        assert exc.response_data == response_data

    def test_api_error_all_params(self):
        """Test APIError with all parameters."""
        response_data = {"error": "Server error"}
        exc = APIError(
            "Server error occurred",
            status_code=500,
            response_data=response_data
        )

        assert str(exc) == "Server error occurred"
        assert exc.status_code == 500
        assert exc.response_data == response_data


@pytest.mark.unit
class TestNetworkError:
    """Tests for NetworkError."""

    def test_network_error(self):
        """Test NetworkError creation."""
        exc = NetworkError("Connection failed")
        assert str(exc) == "Connection failed"
        assert isinstance(exc, MineruException)

    def test_network_error_with_original(self):
        """Test NetworkError with original exception."""
        import requests
        original = requests.ConnectionError("Network unreachable")
        exc = NetworkError("Failed to connect", original_exception=original)

        assert exc.message == "Failed to connect"
        assert exc.original_exception == original


@pytest.mark.unit
class TestConfigurationError:
    """Tests for ConfigurationError."""

    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        exc = ConfigurationError("Invalid configuration")
        assert str(exc) == "Invalid configuration"
        assert isinstance(exc, MineruException)


@pytest.mark.unit
class TestFileOperationError:
    """Tests for FileOperationError."""

    def test_file_operation_error_basic(self):
        """Test basic FileOperationError creation."""
        exc = FileOperationError("File operation failed")
        assert str(exc) == "File operation failed"
        assert exc.file_path is None

    def test_file_operation_error_with_path(self):
        """Test FileOperationError with file path."""
        exc = FileOperationError("Cannot read file", file_path="/path/to/file.pdf")
        assert exc.file_path == "/path/to/file.pdf"

    def test_file_operation_error_with_original(self):
        """Test FileOperationError with original exception."""
        original = IOError("Permission denied")
        exc = FileOperationError(
            "Cannot write file",
            file_path="/path/to/file.pdf",
            original_exception=original
        )

        assert exc.file_path == "/path/to/file.pdf"
        assert exc.original_exception == original


@pytest.mark.unit
class TestUploadError:
    """Tests for UploadError."""

    def test_upload_error_basic(self):
        """Test basic UploadError creation."""
        exc = UploadError("Upload failed")
        assert str(exc) == "Upload failed"
        assert exc.filename is None

    def test_upload_error_with_filename(self):
        """Test UploadError with filename."""
        exc = UploadError("Upload failed", filename="document.pdf")
        assert exc.filename == "document.pdf"

    def test_upload_error_with_original(self):
        """Test UploadError with original exception."""
        import requests
        original = requests.Timeout("Upload timeout")
        exc = UploadError(
            "Upload timed out",
            filename="large_file.pdf",
            original_exception=original
        )

        assert exc.filename == "large_file.pdf"
        assert exc.original_exception == original


@pytest.mark.unit
class TestDownloadError:
    """Tests for DownloadError."""

    def test_download_error_basic(self):
        """Test basic DownloadError creation."""
        exc = DownloadError("Download failed")
        assert str(exc) == "Download failed"
        assert exc.url is None

    def test_download_error_with_url(self):
        """Test DownloadError with URL."""
        exc = DownloadError(
            "Download failed",
            url="https://example.com/file.zip"
        )
        assert exc.url == "https://example.com/file.zip"

    def test_download_error_with_original(self):
        """Test DownloadError with original exception."""
        import requests
        original = requests.ConnectionError("Connection lost")
        exc = DownloadError(
            "Download interrupted",
            url="https://example.com/file.zip",
            original_exception=original
        )

        assert exc.url == "https://example.com/file.zip"
        assert exc.original_exception == original


@pytest.mark.unit
class TestBatchProcessingError:
    """Tests for BatchProcessingError."""

    def test_batch_processing_error_basic(self):
        """Test basic BatchProcessingError creation."""
        exc = BatchProcessingError("Batch processing failed")
        assert str(exc) == "Batch processing failed"
        assert exc.batch_id is None

    def test_batch_processing_error_with_batch_id(self):
        """Test BatchProcessingError with batch ID."""
        exc = BatchProcessingError(
            "Processing failed",
            batch_id="batch_123"
        )
        assert exc.batch_id == "batch_123"

    def test_batch_processing_error_with_original(self):
        """Test BatchProcessingError with original exception."""
        original = Exception("Server error")
        exc = BatchProcessingError(
            "Batch failed",
            batch_id="batch_456",
            original_exception=original
        )

        assert exc.batch_id == "batch_456"
        assert exc.original_exception == original


@pytest.mark.unit
class TestExceptionInheritance:
    """Tests for exception inheritance hierarchy."""

    def test_all_inherit_from_mineru_exception(self):
        """Test that all custom exceptions inherit from MineruException."""
        exceptions = [
            ValidationError,
            AuthenticationError,
            APIError,
            NetworkError,
            ConfigurationError,
            FileOperationError,
            UploadError,
            DownloadError,
            BatchProcessingError
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, MineruException)

    def test_all_inherit_from_base_exception(self):
        """Test that all custom exceptions inherit from base Exception."""
        exceptions = [
            MineruException,
            ValidationError,
            AuthenticationError,
            APIError,
            NetworkError,
            ConfigurationError,
            FileOperationError,
            UploadError,
            DownloadError,
            BatchProcessingError
        ]

        for exc_class in exceptions:
            assert issubclass(exc_class, Exception)

    def test_exception_can_be_caught_as_mineru_exception(self):
        """Test that custom exceptions can be caught as MineruException."""
        try:
            raise ValidationError("Test error")
        except MineruException as e:
            assert isinstance(e, ValidationError)
            assert str(e) == "Test error"

    def test_exception_can_be_caught_as_base_exception(self):
        """Test that custom exceptions can be caught as Exception."""
        try:
            raise APIError("Test error", status_code=500)
        except Exception as e:
            assert isinstance(e, APIError)
            assert e.status_code == 500
