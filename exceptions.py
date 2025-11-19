"""Custom exceptions for MinerU Desktop Client.

This module defines custom exception classes to provide more specific error handling
throughout the application. All exceptions inherit from MinerUException for
easy catching of application-specific errors.

Exception Hierarchy:
    MinerUException (base)
    ├── ConfigurationError (invalid or missing configuration)
    ├── AuthenticationError (API token issues, 401/403 errors)
    ├── ValidationError (input validation failures)
    ├── APIError (API request failures with status codes)
    ├── NetworkError (connectivity issues, timeouts)
    ├── FileOperationError (file I/O failures)
    ├── UploadError (file upload specific failures)
    └── DownloadError (file download specific failures)

Usage Example:
    >>> from exceptions import AuthenticationError
    >>> try:
    ...     client.upload_batch(files)
    ... except AuthenticationError as e:
    ...     print("Please configure API token in Settings")
    ... except NetworkError as e:
    ...     print("Check your internet connection")
    ... except MinerUException as e:
    ...     print(f"Application error: {e}")

Best Practices:
    - Catch specific exceptions when you can handle them specifically
    - Use MinerUException to catch all app errors generically
    - Re-raise exceptions after logging if you can't handle them
    - Include context in exception messages

For error handling patterns, see docs/PATTERNS.md#error-handling
"""


class MinerUException(Exception):
    """Base exception for all MinerU-related errors.

    All custom exceptions in this application inherit from this class,
    allowing for easy catching of all application-specific errors.

    Example:
        >>> try:
        ...     do_something()
        ... except MinerUException as e:
        ...     logger.error(f"Application error: {e}")
    """
    pass


class ConfigurationError(MinerUException):
    """Raised when there's a configuration-related error."""
    pass


class AuthenticationError(MinerUException):
    """Raised when authentication fails."""
    pass


class ValidationError(MinerUException):
    """Raised when data validation fails."""
    pass


class APIError(MinerUException):
    """Raised when an API request fails.

    Includes HTTP status code and response data for detailed error analysis.

    Attributes:
        status_code (int): HTTP status code (e.g., 400, 500)
        response_data (str): Raw response body from API

    Example:
        >>> try:
        ...     client.get_batch_status('invalid')
        ... except APIError as e:
        ...     if e.status_code == 404:
        ...         print("Batch not found")
        ...     else:
        ...         print(f"API error {e.status_code}: {e}")
    """

    def __init__(self, message, status_code=None, response_data=None):
        """Initialize APIError with optional status code and response data.

        Args:
            message: Error message describing the failure
            status_code: HTTP status code (optional)
            response_data: Raw API response text (optional)
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class NetworkError(MinerUException):
    """Raised when network connectivity issues occur."""
    pass


class FileOperationError(MinerUException):
    """Raised when file operations fail."""
    pass


class UploadError(MinerUException):
    """Raised when file upload fails."""
    pass


class DownloadError(MinerUException):
    """Raised when file download fails."""
    pass


class BatchProcessingError(MinerUException):
    """Raised when batch processing encounters an error."""
    pass
