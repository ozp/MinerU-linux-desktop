"""Input validators for MinerU Desktop Client.

This module provides validation functions for various inputs including
file paths, API tokens, and configuration values. All validators raise
ValidationError on invalid input.

Validation Functions:
    - validate_api_token: API token format and length
    - validate_file_path: File existence and accessibility
    - validate_directory_path: Directory existence (with optional creation)
    - validate_file_format: Supported file formats (PDF, DOCX, etc.)
    - validate_batch_id: Batch ID format
    - validate_language_code: Language code (pt, en, ch)
    - validate_model_version: Model version (pipeline, vlm)

All validators follow a consistent pattern:
    1. Accept input value
    2. Validate against rules
    3. Return sanitized value on success
    4. Raise ValidationError on failure

Example:
    >>> from validators import validate_file_path, validate_api_token
    >>> try:
    ...     path = validate_file_path('/path/to/doc.pdf')
    ...     token = validate_api_token('abc123...')
    ... except ValidationError as e:
    ...     print(f"Invalid input: {e}")

Best Practices:
    - Always validate user input before processing
    - Use validators before making API calls
    - Catch ValidationError to show user-friendly messages
    - Validators are pure functions (no side effects except create_if_missing)

For validation patterns, see docs/PATTERNS.md#input-validation
"""
import os
import re
from typing import List
from exceptions import ValidationError


def validate_api_token(token: str) -> str:
    """
    Validate API token format.

    Args:
        token: API token string

    Returns:
        str: Validated token

    Raises:
        ValidationError: If token is invalid
    """
    if not token or not isinstance(token, str):
        raise ValidationError("API token must be a non-empty string")

    token = token.strip()

    if len(token) < 10:
        raise ValidationError("API token is too short (minimum 10 characters)")

    if len(token) > 512:
        raise ValidationError("API token is too long (maximum 512 characters)")

    # Check for invalid characters (basic validation)
    if not re.match(r'^[A-Za-z0-9_\-\.]+$', token):
        raise ValidationError("API token contains invalid characters")

    return token


def validate_file_path(file_path: str) -> str:
    """
    Validate that a file path exists and is accessible.

    Args:
        file_path: Path to file

    Returns:
        str: Validated absolute file path

    Raises:
        ValidationError: If path is invalid
    """
    if not file_path or not isinstance(file_path, str):
        raise ValidationError("File path must be a non-empty string")

    file_path = file_path.strip()

    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")

    if not os.path.isfile(file_path):
        raise ValidationError(f"Path is not a file: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise ValidationError(f"File is not readable: {file_path}")

    return os.path.abspath(file_path)


def validate_directory_path(dir_path: str, create_if_missing: bool = False) -> str:
    """
    Validate that a directory path exists and is accessible.

    Args:
        dir_path: Path to directory
        create_if_missing: Whether to create directory if it doesn't exist

    Returns:
        str: Validated absolute directory path

    Raises:
        ValidationError: If path is invalid
    """
    if not dir_path or not isinstance(dir_path, str):
        raise ValidationError("Directory path must be a non-empty string")

    dir_path = os.path.expanduser(dir_path.strip())

    if not os.path.exists(dir_path):
        if create_if_missing:
            try:
                os.makedirs(dir_path, exist_ok=True)
            except OSError as e:
                raise ValidationError(f"Cannot create directory: {e}")
        else:
            raise ValidationError(f"Directory does not exist: {dir_path}")

    if not os.path.isdir(dir_path):
        raise ValidationError(f"Path is not a directory: {dir_path}")

    if not os.access(dir_path, os.W_OK):
        raise ValidationError(f"Directory is not writable: {dir_path}")

    return os.path.abspath(dir_path)


def validate_file_format(file_path: str, allowed_extensions: List[str] = None) -> str:
    """
    Validate file format based on extension.

    Args:
        file_path: Path to file
        allowed_extensions: List of allowed extensions (e.g., ['.pdf', '.docx'])

    Returns:
        str: File extension

    Raises:
        ValidationError: If file format is not allowed
    """
    if allowed_extensions is None:
        allowed_extensions = ['.pdf', '.docx', '.pptx', '.jpg', '.jpeg', '.png']

    file_path = validate_file_path(file_path)
    _, ext = os.path.splitext(file_path)
    ext = ext.lower()

    if ext not in allowed_extensions:
        raise ValidationError(
            f"File format '{ext}' not supported. "
            f"Allowed formats: {', '.join(allowed_extensions)}"
        )

    return ext


def validate_batch_id(batch_id: str) -> str:
    """
    Validate batch ID format.

    Args:
        batch_id: Batch ID string

    Returns:
        str: Validated batch ID

    Raises:
        ValidationError: If batch ID is invalid
    """
    if not batch_id or not isinstance(batch_id, str):
        raise ValidationError("Batch ID must be a non-empty string")

    batch_id = batch_id.strip()

    if len(batch_id) < 5:
        raise ValidationError("Batch ID is too short")

    if len(batch_id) > 128:
        raise ValidationError("Batch ID is too long")

    return batch_id


def validate_language_code(language: str) -> str:
    """
    Validate language code.

    Args:
        language: Language code (e.g., 'en', 'pt', 'ch')

    Returns:
        str: Validated language code

    Raises:
        ValidationError: If language code is invalid
    """
    allowed_languages = ['en', 'pt', 'ch']

    if not language or not isinstance(language, str):
        raise ValidationError("Language code must be a non-empty string")

    language = language.strip().lower()

    if language not in allowed_languages:
        raise ValidationError(
            f"Language '{language}' not supported. "
            f"Allowed languages: {', '.join(allowed_languages)}"
        )

    return language


def validate_model_version(model_version: str) -> str:
    """
    Validate model version.

    Args:
        model_version: Model version ('pipeline' or 'vlm')

    Returns:
        str: Validated model version

    Raises:
        ValidationError: If model version is invalid
    """
    allowed_models = ['pipeline', 'vlm']

    if not model_version or not isinstance(model_version, str):
        raise ValidationError("Model version must be a non-empty string")

    model_version = model_version.strip().lower()

    if model_version not in allowed_models:
        raise ValidationError(
            f"Model version '{model_version}' not supported. "
            f"Allowed models: {', '.join(allowed_models)}"
        )

    return model_version
