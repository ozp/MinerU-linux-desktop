"""
Pytest configuration and fixtures for MinerU Desktop Client tests.

This module provides shared fixtures and configuration for all test modules.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Generator
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from mineru_desktop.models.batch import (
    Batch,
    FileStatus,
    ProcessingOptions,
    ModelVersion,
    Language,
    FileState
)
from mineru_desktop.core.client import MineruClient
from mineru_desktop.core.config import ConfigManager


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def temp_config_file(temp_dir: str) -> str:
    """Create a temporary config file path."""
    return os.path.join(temp_dir, "test_config.ini")


@pytest.fixture
def sample_api_token() -> str:
    """Provide a sample API token for testing."""
    return "test_token_12345"


@pytest.fixture
def sample_processing_options() -> ProcessingOptions:
    """Create sample processing options."""
    return ProcessingOptions(
        is_ocr=True,
        enable_formula=False,
        enable_table=True,
        language=Language.PORTUGUESE,
        model_version=ModelVersion.PIPELINE
    )


@pytest.fixture
def sample_batch(sample_processing_options: ProcessingOptions) -> Batch:
    """Create a sample batch for testing."""
    batch = Batch(
        batch_id="batch_123",
        processing_options=sample_processing_options
    )
    return batch


@pytest.fixture
def sample_file_status() -> FileStatus:
    """Create a sample file status."""
    return FileStatus(
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        state=FileState.READY
    )


@pytest.fixture
def mock_client(sample_api_token: str) -> MineruClient:
    """Create a MinerU client with mock token."""
    return MineruClient(api_token=sample_api_token)


@pytest.fixture
def config_manager(temp_config_file: str) -> ConfigManager:
    """Create a ConfigManager with temporary config file."""
    return ConfigManager(config_file=temp_config_file)


@pytest.fixture
def sample_files(temp_dir: str) -> list[str]:
    """Create sample PDF files for testing."""
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"test_{i}.pdf")
        # Create dummy PDF file
        with open(file_path, "wb") as f:
            f.write(b"%PDF-1.4\n%fake pdf content")
        files.append(file_path)
    return files


@pytest.fixture
def mock_batch_response() -> dict:
    """Mock response from batch upload API."""
    return {
        "data": {
            "batch_id": "batch_123",
            "file_urls": [
                "https://example.com/upload/1",
                "https://example.com/upload/2",
                "https://example.com/upload/3"
            ]
        }
    }


@pytest.fixture
def mock_status_response() -> dict:
    """Mock response from batch status API."""
    return {
        "data": {
            "batch_id": "batch_123",
            "status": "completed",
            "files": [
                {
                    "filename": "test_0.pdf",
                    "status": "done",
                    "zip_url": "https://example.com/result/1.zip"
                },
                {
                    "filename": "test_1.pdf",
                    "status": "done",
                    "zip_url": "https://example.com/result/2.zip"
                },
                {
                    "filename": "test_2.pdf",
                    "status": "processing",
                    "zip_url": None
                }
            ]
        }
    }


@pytest.fixture(autouse=True)
def reset_logging():
    """Reset logging configuration for each test."""
    import logging
    # Clear all handlers
    logger = logging.getLogger()
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    yield
    # Cleanup after test
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
