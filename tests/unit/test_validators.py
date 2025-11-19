"""Unit tests for validators module."""
import os
import tempfile
import pytest
from validators import (
    validate_api_token, validate_file_path, validate_directory_path,
    validate_file_format, validate_batch_id, validate_language_code,
    validate_model_version
)
from exceptions import ValidationError


@pytest.mark.unit
class TestValidateApiToken:
    """Tests for API token validation."""

    def test_valid_token(self):
        """Test validation of a valid API token."""
        token = "abcdef1234567890"
        result = validate_api_token(token)
        assert result == token

    def test_valid_token_with_special_chars(self):
        """Test validation of token with allowed special characters."""
        token = "abc-def_123.456"
        result = validate_api_token(token)
        assert result == token

    def test_empty_token(self):
        """Test validation fails for empty token."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_api_token("")

    def test_none_token(self):
        """Test validation fails for None token."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_api_token(None)

    def test_short_token(self):
        """Test validation fails for too short token."""
        with pytest.raises(ValidationError, match="too short"):
            validate_api_token("abc")

    def test_long_token(self):
        """Test validation fails for too long token."""
        with pytest.raises(ValidationError, match="too long"):
            validate_api_token("a" * 600)

    def test_invalid_characters(self):
        """Test validation fails for invalid characters."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_api_token("token@with#special!")

    def test_token_with_whitespace_stripped(self):
        """Test that whitespace is stripped from token."""
        token = "  valid_token_123  "
        result = validate_api_token(token)
        assert result == "valid_token_123"


@pytest.mark.unit
class TestValidateFilePath:
    """Tests for file path validation."""

    def test_valid_file_path(self, sample_pdf_file):
        """Test validation of a valid file path."""
        result = validate_file_path(sample_pdf_file)
        assert os.path.isabs(result)
        assert os.path.exists(result)

    def test_nonexistent_file(self):
        """Test validation fails for non-existent file."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_file_path("/nonexistent/file.pdf")

    def test_directory_instead_of_file(self, temp_dir):
        """Test validation fails for directory path."""
        with pytest.raises(ValidationError, match="not a file"):
            validate_file_path(temp_dir)

    def test_empty_path(self):
        """Test validation fails for empty path."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_file_path("")

    def test_none_path(self):
        """Test validation fails for None path."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_file_path(None)


@pytest.mark.unit
class TestValidateDirectoryPath:
    """Tests for directory path validation."""

    def test_valid_directory(self, temp_dir):
        """Test validation of a valid directory."""
        result = validate_directory_path(temp_dir)
        assert os.path.isabs(result)
        assert os.path.isdir(result)

    def test_create_missing_directory(self, temp_dir):
        """Test creation of missing directory."""
        new_dir = os.path.join(temp_dir, "new_subdir")
        result = validate_directory_path(new_dir, create_if_missing=True)
        assert os.path.exists(result)
        assert os.path.isdir(result)

    def test_missing_directory_no_create(self):
        """Test validation fails for missing directory when not creating."""
        with pytest.raises(ValidationError, match="does not exist"):
            validate_directory_path("/nonexistent/directory", create_if_missing=False)

    def test_file_instead_of_directory(self, sample_pdf_file):
        """Test validation fails when path is a file."""
        with pytest.raises(ValidationError, match="not a directory"):
            validate_directory_path(sample_pdf_file)

    def test_expand_user_path(self, monkeypatch, temp_dir):
        """Test that ~ is expanded in paths."""
        monkeypatch.setenv("HOME", temp_dir)
        result = validate_directory_path("~", create_if_missing=False)
        assert result == temp_dir


@pytest.mark.unit
class TestValidateFileFormat:
    """Tests for file format validation."""

    def test_valid_pdf_format(self, temp_dir):
        """Test validation of PDF file."""
        pdf_file = os.path.join(temp_dir, "test.pdf")
        with open(pdf_file, 'w') as f:
            f.write("test")
        result = validate_file_format(pdf_file)
        assert result == ".pdf"

    def test_valid_docx_format(self, temp_dir):
        """Test validation of DOCX file."""
        docx_file = os.path.join(temp_dir, "test.docx")
        with open(docx_file, 'w') as f:
            f.write("test")
        result = validate_file_format(docx_file)
        assert result == ".docx"

    def test_invalid_format(self, temp_dir):
        """Test validation fails for unsupported format."""
        txt_file = os.path.join(temp_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("test")
        with pytest.raises(ValidationError, match="not supported"):
            validate_file_format(txt_file)

    def test_custom_allowed_extensions(self, temp_dir):
        """Test validation with custom allowed extensions."""
        txt_file = os.path.join(temp_dir, "test.txt")
        with open(txt_file, 'w') as f:
            f.write("test")
        result = validate_file_format(txt_file, allowed_extensions=['.txt'])
        assert result == ".txt"

    def test_case_insensitive_extension(self, temp_dir):
        """Test that file extensions are case-insensitive."""
        pdf_file = os.path.join(temp_dir, "test.PDF")
        with open(pdf_file, 'w') as f:
            f.write("test")
        result = validate_file_format(pdf_file)
        assert result == ".pdf"


@pytest.mark.unit
class TestValidateBatchId:
    """Tests for batch ID validation."""

    def test_valid_batch_id(self):
        """Test validation of a valid batch ID."""
        batch_id = "batch_123456"
        result = validate_batch_id(batch_id)
        assert result == batch_id

    def test_empty_batch_id(self):
        """Test validation fails for empty batch ID."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_batch_id("")

    def test_none_batch_id(self):
        """Test validation fails for None batch ID."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_batch_id(None)

    def test_short_batch_id(self):
        """Test validation fails for too short batch ID."""
        with pytest.raises(ValidationError, match="too short"):
            validate_batch_id("abc")

    def test_long_batch_id(self):
        """Test validation fails for too long batch ID."""
        with pytest.raises(ValidationError, match="too long"):
            validate_batch_id("a" * 200)

    def test_batch_id_with_whitespace_stripped(self):
        """Test that whitespace is stripped from batch ID."""
        batch_id = "  batch_123  "
        result = validate_batch_id(batch_id)
        assert result == "batch_123"


@pytest.mark.unit
class TestValidateLanguageCode:
    """Tests for language code validation."""

    def test_valid_english(self):
        """Test validation of English language code."""
        result = validate_language_code("en")
        assert result == "en"

    def test_valid_portuguese(self):
        """Test validation of Portuguese language code."""
        result = validate_language_code("pt")
        assert result == "pt"

    def test_valid_chinese(self):
        """Test validation of Chinese language code."""
        result = validate_language_code("ch")
        assert result == "ch"

    def test_invalid_language(self):
        """Test validation fails for unsupported language."""
        with pytest.raises(ValidationError, match="not supported"):
            validate_language_code("fr")

    def test_empty_language(self):
        """Test validation fails for empty language."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_language_code("")

    def test_case_insensitive(self):
        """Test that language codes are case-insensitive."""
        result = validate_language_code("EN")
        assert result == "en"


@pytest.mark.unit
class TestValidateModelVersion:
    """Tests for model version validation."""

    def test_valid_pipeline(self):
        """Test validation of pipeline model."""
        result = validate_model_version("pipeline")
        assert result == "pipeline"

    def test_valid_vlm(self):
        """Test validation of VLM model."""
        result = validate_model_version("vlm")
        assert result == "vlm"

    def test_invalid_model(self):
        """Test validation fails for unsupported model."""
        with pytest.raises(ValidationError, match="not supported"):
            validate_model_version("gpt4")

    def test_empty_model(self):
        """Test validation fails for empty model."""
        with pytest.raises(ValidationError, match="non-empty string"):
            validate_model_version("")

    def test_case_insensitive(self):
        """Test that model versions are case-insensitive."""
        result = validate_model_version("PIPELINE")
        assert result == "pipeline"
