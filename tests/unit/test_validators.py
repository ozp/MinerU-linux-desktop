"""
Unit tests for validation utilities.

Tests all validation functions for proper input checking
and error handling.
"""

import os
import pytest
import tempfile
from pathlib import Path

from mineru_desktop.utils.validators import (
    validate_api_token,
    validate_file_path,
    validate_file_extension,
    validate_file_size,
    validate_directory_path,
    validate_batch_id,
    validate_file_list,
    validate_url
)
from mineru_desktop.core.exceptions import ValidationError


@pytest.mark.unit
class TestAPITokenValidation:
    """Tests for API token validation."""

    def test_validate_api_token_valid(self):
        """Test validation of valid API tokens."""
        valid_tokens = [
            "test_token_123",
            "ABCDEFGHIJK",
            "token-with-hyphens",
            "token_with_underscores",
            "token.with.dots",
            "a" * 50,  # Long token
        ]

        for token in valid_tokens:
            validate_api_token(token)  # Should not raise

    def test_validate_api_token_empty(self):
        """Test validation of empty token."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_token("")

    def test_validate_api_token_none(self):
        """Test validation of None token."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_api_token(None)

    def test_validate_api_token_too_short(self):
        """Test validation of too short token."""
        with pytest.raises(ValidationError, match="at least .* characters"):
            validate_api_token("short")

    def test_validate_api_token_invalid_characters(self):
        """Test validation of token with invalid characters."""
        invalid_tokens = [
            "token with spaces",
            "token@email.com",
            "token#hash",
            "token/slash",
        ]

        for token in invalid_tokens:
            with pytest.raises(ValidationError, match="invalid characters"):
                validate_api_token(token)

    def test_validate_api_token_not_string(self):
        """Test validation of non-string token."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_api_token(123)


@pytest.mark.unit
class TestFilePathValidation:
    """Tests for file path validation."""

    def test_validate_file_path_valid(self, sample_files):
        """Test validation of valid file paths."""
        for file_path in sample_files:
            validate_file_path(file_path)  # Should not raise

    def test_validate_file_path_empty(self):
        """Test validation of empty path."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_path("")

    def test_validate_file_path_not_exists(self):
        """Test validation of non-existent file."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_file_path("/nonexistent/file.pdf")

    def test_validate_file_path_is_directory(self, temp_dir):
        """Test validation of directory path as file."""
        with pytest.raises(ValidationError, match="not a file"):
            validate_file_path(temp_dir)

    def test_validate_file_path_not_readable(self, temp_dir):
        """Test validation of non-readable file."""
        # Skip this test if running as root (root can read any file)
        if os.geteuid() == 0:
            pytest.skip("Test cannot run as root user")

        file_path = os.path.join(temp_dir, "unreadable.pdf")
        with open(file_path, "w") as f:
            f.write("test")

        # Change permissions to make unreadable (Unix only)
        if os.name != 'nt':  # Skip on Windows
            os.chmod(file_path, 0o000)
            with pytest.raises(ValidationError, match="not readable"):
                validate_file_path(file_path)
            # Restore permissions for cleanup
            os.chmod(file_path, 0o644)


@pytest.mark.unit
class TestFileExtensionValidation:
    """Tests for file extension validation."""

    def test_validate_file_extension_pdf(self, sample_files):
        """Test validation of PDF files."""
        for file_path in sample_files:
            validate_file_extension(file_path)  # Should not raise

    def test_validate_file_extension_invalid(self):
        """Test validation of non-PDF files."""
        invalid_files = [
            "/path/to/file.txt",
            "/path/to/file.doc",
            "/path/to/file.jpg",
        ]

        for file_path in invalid_files:
            with pytest.raises(ValidationError, match="Unsupported file type"):
                validate_file_extension(file_path)

    def test_validate_file_extension_custom_allowed(self):
        """Test validation with custom allowed extensions."""
        allowed_extensions = {'.txt', '.pdf'}

        # Should pass
        validate_file_extension("/path/to/file.txt", allowed_extensions)
        validate_file_extension("/path/to/file.pdf", allowed_extensions)

        # Should fail
        with pytest.raises(ValidationError):
            validate_file_extension("/path/to/file.jpg", allowed_extensions)


@pytest.mark.unit
class TestFileSizeValidation:
    """Tests for file size validation."""

    def test_validate_file_size_valid(self, sample_files):
        """Test validation of files within size limit."""
        for file_path in sample_files:
            validate_file_size(file_path, max_size_mb=100)  # Should not raise

    def test_validate_file_size_too_large(self, temp_dir):
        """Test validation of oversized file."""
        large_file = os.path.join(temp_dir, "large.pdf")

        # Create a 2MB file
        with open(large_file, "wb") as f:
            f.write(b"0" * (2 * 1024 * 1024))

        # Should fail with 1MB limit
        with pytest.raises(ValidationError, match="too large"):
            validate_file_size(large_file, max_size_mb=1)

    def test_validate_file_size_empty_file(self, temp_dir):
        """Test validation of empty file."""
        empty_file = os.path.join(temp_dir, "empty.pdf")
        with open(empty_file, "w") as f:
            pass  # Create empty file

        with pytest.raises(ValidationError, match="empty"):
            validate_file_size(empty_file)


@pytest.mark.unit
class TestDirectoryPathValidation:
    """Tests for directory path validation."""

    def test_validate_directory_path_valid(self, temp_dir):
        """Test validation of valid directory."""
        validate_directory_path(temp_dir)  # Should not raise

    def test_validate_directory_path_empty(self):
        """Test validation of empty path."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_directory_path("")

    def test_validate_directory_path_not_exists(self):
        """Test validation of non-existent directory."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_directory_path("/nonexistent/directory")

    def test_validate_directory_path_create_if_missing(self, temp_dir):
        """Test creating directory if missing."""
        new_dir = os.path.join(temp_dir, "new_directory")

        validate_directory_path(new_dir, create_if_missing=True)

        # Verify directory was created
        assert os.path.exists(new_dir)
        assert os.path.isdir(new_dir)

    def test_validate_directory_path_is_file(self, sample_files):
        """Test validation of file path as directory."""
        with pytest.raises(ValidationError, match="not a directory"):
            validate_directory_path(sample_files[0])

    def test_validate_directory_path_tilde_expansion(self):
        """Test that tilde is expanded in path."""
        # This should expand ~ and check the home directory
        validate_directory_path("~", create_if_missing=False)


@pytest.mark.unit
class TestBatchIDValidation:
    """Tests for batch ID validation."""

    def test_validate_batch_id_valid(self):
        """Test validation of valid batch IDs."""
        valid_ids = [
            "batch_123",
            "abc-def-ghi",
            "BATCH_ID_1",
        ]

        for batch_id in valid_ids:
            validate_batch_id(batch_id)  # Should not raise

    def test_validate_batch_id_empty(self):
        """Test validation of empty batch ID."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_batch_id("")

    def test_validate_batch_id_whitespace(self):
        """Test validation of whitespace-only batch ID."""
        with pytest.raises(ValidationError, match="cannot be whitespace"):
            validate_batch_id("   ")

    def test_validate_batch_id_not_string(self):
        """Test validation of non-string batch ID."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_batch_id(123)


@pytest.mark.unit
class TestFileListValidation:
    """Tests for file list validation."""

    def test_validate_file_list_valid(self, sample_files):
        """Test validation of valid file list."""
        validate_file_list(sample_files)  # Should not raise

    def test_validate_file_list_empty(self):
        """Test validation of empty file list."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_file_list([])

    def test_validate_file_list_too_many_files(self, temp_dir):
        """Test validation of too many files."""
        # Create 5 files
        files = []
        for i in range(5):
            file_path = os.path.join(temp_dir, f"file_{i}.pdf")
            with open(file_path, "wb") as f:
                f.write(b"%PDF-1.4\ntest")
            files.append(file_path)

        # Should fail with max 3 files
        with pytest.raises(ValidationError, match="Too many files"):
            validate_file_list(files, max_files=3)

    def test_validate_file_list_invalid_file(self, sample_files):
        """Test validation with one invalid file."""
        files = sample_files + ["/nonexistent/file.pdf"]

        with pytest.raises(ValidationError):
            validate_file_list(files)

    def test_validate_file_list_not_list(self):
        """Test validation of non-list input."""
        with pytest.raises(ValidationError, match="must be a list"):
            validate_file_list("not_a_list")


@pytest.mark.unit
class TestURLValidation:
    """Tests for URL validation."""

    def test_validate_url_valid(self):
        """Test validation of valid URLs."""
        valid_urls = [
            "https://example.com",
            "http://example.com/path",
            "https://api.example.com/v1/endpoint",
            "https://example.com:8080/path?query=value",
        ]

        for url in valid_urls:
            validate_url(url)  # Should not raise

    def test_validate_url_empty(self):
        """Test validation of empty URL."""
        with pytest.raises(ValidationError, match="cannot be empty"):
            validate_url("")

    def test_validate_url_no_protocol(self):
        """Test validation of URL without protocol."""
        with pytest.raises(ValidationError, match="must start with http"):
            validate_url("example.com")

    def test_validate_url_invalid_protocol(self):
        """Test validation of URL with invalid protocol."""
        with pytest.raises(ValidationError, match="must start with http"):
            validate_url("ftp://example.com")

    def test_validate_url_too_short(self):
        """Test validation of too short URL."""
        with pytest.raises(ValidationError, match="too short"):
            validate_url("http://")

    def test_validate_url_not_string(self):
        """Test validation of non-string URL."""
        with pytest.raises(ValidationError, match="must be a string"):
            validate_url(123)
