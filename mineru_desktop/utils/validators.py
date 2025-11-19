"""
Validation utilities for MinerU Desktop Client.

This module provides robust validation functions for various inputs
throughout the application.
"""

import os
import re
from pathlib import Path
from typing import List, Optional

from mineru_desktop.core.exceptions import ValidationError


# Supported file extensions
SUPPORTED_EXTENSIONS = {'.pdf', '.PDF'}

# API token pattern (alphanumeric and common special chars)
API_TOKEN_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')

# Minimum token length
MIN_TOKEN_LENGTH = 10


def validate_api_token(token: str) -> None:
    """
    Validate API token format.

    Args:
        token: API token to validate

    Raises:
        ValidationError: If token is invalid
    """
    if not token:
        raise ValidationError("API token cannot be empty")

    if not isinstance(token, str):
        raise ValidationError("API token must be a string")

    token = token.strip()

    if len(token) < MIN_TOKEN_LENGTH:
        raise ValidationError(
            f"API token must be at least {MIN_TOKEN_LENGTH} characters long"
        )

    if not API_TOKEN_PATTERN.match(token):
        raise ValidationError(
            "API token contains invalid characters. "
            "Only alphanumeric characters, hyphens, underscores, and dots are allowed"
        )


def validate_file_path(file_path: str) -> None:
    """
    Validate that a file path exists and is accessible.

    Args:
        file_path: Path to validate

    Raises:
        ValidationError: If file path is invalid
    """
    if not file_path:
        raise ValidationError("File path cannot be empty")

    if not isinstance(file_path, str):
        raise ValidationError("File path must be a string")

    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")

    if not os.path.isfile(file_path):
        raise ValidationError(f"Path is not a file: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise ValidationError(f"File is not readable: {file_path}")


def validate_file_extension(file_path: str, allowed_extensions: set = None) -> None:
    """
    Validate file extension.

    Args:
        file_path: Path to file
        allowed_extensions: Set of allowed extensions (default: PDF only)

    Raises:
        ValidationError: If file extension is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = SUPPORTED_EXTENSIONS

    file_ext = Path(file_path).suffix

    if file_ext not in allowed_extensions:
        raise ValidationError(
            f"Unsupported file type: {file_ext}. "
            f"Allowed types: {', '.join(allowed_extensions)}"
        )


def validate_file_size(file_path: str, max_size_mb: int = 100) -> None:
    """
    Validate file size.

    Args:
        file_path: Path to file
        max_size_mb: Maximum allowed size in MB

    Raises:
        ValidationError: If file is too large
    """
    file_size = os.path.getsize(file_path)
    max_size_bytes = max_size_mb * 1024 * 1024

    if file_size > max_size_bytes:
        actual_size_mb = file_size / (1024 * 1024)
        raise ValidationError(
            f"File is too large: {actual_size_mb:.2f} MB. "
            f"Maximum allowed size: {max_size_mb} MB"
        )

    if file_size == 0:
        raise ValidationError(f"File is empty: {file_path}")


def validate_directory_path(dir_path: str, create_if_missing: bool = False) -> None:
    """
    Validate directory path.

    Args:
        dir_path: Directory path to validate
        create_if_missing: Create directory if it doesn't exist

    Raises:
        ValidationError: If directory is invalid
    """
    if not dir_path:
        raise ValidationError("Directory path cannot be empty")

    if not isinstance(dir_path, str):
        raise ValidationError("Directory path must be a string")

    expanded_path = os.path.expanduser(dir_path)

    if not os.path.exists(expanded_path):
        if create_if_missing:
            try:
                Path(expanded_path).mkdir(parents=True, exist_ok=True)
            except Exception as e:
                raise ValidationError(
                    f"Failed to create directory: {expanded_path}"
                ) from e
        else:
            raise ValidationError(f"Directory does not exist: {expanded_path}")

    if not os.path.isdir(expanded_path):
        raise ValidationError(f"Path is not a directory: {expanded_path}")

    if not os.access(expanded_path, os.W_OK):
        raise ValidationError(f"Directory is not writable: {expanded_path}")


def validate_batch_id(batch_id: str) -> None:
    """
    Validate batch ID format.

    Args:
        batch_id: Batch ID to validate

    Raises:
        ValidationError: If batch ID is invalid
    """
    if not batch_id:
        raise ValidationError("Batch ID cannot be empty")

    if not isinstance(batch_id, str):
        raise ValidationError("Batch ID must be a string")

    if len(batch_id.strip()) == 0:
        raise ValidationError("Batch ID cannot be whitespace only")


def validate_file_list(file_paths: List[str], max_files: int = 100) -> None:
    """
    Validate a list of file paths.

    Args:
        file_paths: List of file paths to validate
        max_files: Maximum number of files allowed

    Raises:
        ValidationError: If file list is invalid
    """
    if not file_paths:
        raise ValidationError("File list cannot be empty")

    if not isinstance(file_paths, (list, tuple)):
        raise ValidationError("File paths must be a list or tuple")

    if len(file_paths) > max_files:
        raise ValidationError(
            f"Too many files: {len(file_paths)}. Maximum allowed: {max_files}"
        )

    for file_path in file_paths:
        validate_file_path(file_path)
        validate_file_extension(file_path)


def validate_url(url: str) -> None:
    """
    Validate URL format.

    Args:
        url: URL to validate

    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError("URL cannot be empty")

    if not isinstance(url, str):
        raise ValidationError("URL must be a string")

    url = url.strip()

    if not url.startswith(('http://', 'https://')):
        raise ValidationError("URL must start with http:// or https://")

    if len(url) < 10:
        raise ValidationError("URL is too short to be valid")
