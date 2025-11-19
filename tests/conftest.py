"""Pytest configuration and shared fixtures."""
import os
import tempfile
import pytest
from unittest.mock import MagicMock


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_config_file(temp_dir):
    """Provide a temporary config file path."""
    return os.path.join(temp_dir, "config.ini")


@pytest.fixture
def sample_pdf_file(temp_dir):
    """Create a sample PDF file for testing."""
    pdf_path = os.path.join(temp_dir, "sample.pdf")
    with open(pdf_path, 'wb') as f:
        f.write(b'%PDF-1.4 fake pdf content')
    return pdf_path


@pytest.fixture
def sample_files(temp_dir):
    """Create multiple sample files for batch testing."""
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"document_{i}.pdf")
        with open(file_path, 'wb') as f:
            f.write(b'%PDF-1.4 fake pdf content')
        files.append(file_path)
    return files


@pytest.fixture
def mock_keyring(monkeypatch):
    """Mock keyring for secure storage tests."""
    mock_get = MagicMock(return_value="test_token_12345")
    mock_set = MagicMock()

    monkeypatch.setattr("keyring.get_password", mock_get)
    monkeypatch.setattr("keyring.set_password", mock_set)

    return {"get": mock_get, "set": mock_set}


@pytest.fixture
def api_response_batch():
    """Sample API response for batch upload."""
    return {
        "data": {
            "batch_id": "batch_123456",
            "file_urls": [
                "https://s3.example.com/upload1",
                "https://s3.example.com/upload2",
                "https://s3.example.com/upload3"
            ]
        }
    }


@pytest.fixture
def api_response_status_processing():
    """Sample API response for batch status (processing)."""
    return {
        "data": {
            "extract_result": [
                {
                    "file_name": "document_0.pdf",
                    "state": "processing"
                },
                {
                    "file_name": "document_1.pdf",
                    "state": "pending"
                },
                {
                    "file_name": "document_2.pdf",
                    "state": "processing"
                }
            ]
        }
    }


@pytest.fixture
def api_response_status_done():
    """Sample API response for batch status (done)."""
    return {
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
                    "state": "failed",
                    "err_msg": "Processing error"
                }
            ]
        }
    }
