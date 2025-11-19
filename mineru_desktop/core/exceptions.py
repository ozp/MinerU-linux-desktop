"""
Custom exception classes for MinerU Desktop Client.

This module provides specialized exception types for better error handling
and more informative error messages throughout the application.
"""


class MineruException(Exception):
    """Base exception for all MinerU Desktop Client errors."""

    def __init__(self, message: str, original_exception: Exception = None):
        """
        Initialize MinerU exception.

        Args:
            message: Error message
            original_exception: Optional original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.original_exception = original_exception


class ValidationError(MineruException):
    """Raised when input validation fails."""
    pass


class AuthenticationError(MineruException):
    """Raised when API authentication fails."""
    pass


class APIError(MineruException):
    """Raised when API requests fail."""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        """
        Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
            response_data: Response data from API
        """
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class NetworkError(MineruException):
    """Raised when network operations fail."""
    pass


class ConfigurationError(MineruException):
    """Raised when configuration is invalid or missing."""
    pass


class FileOperationError(MineruException):
    """Raised when file operations fail."""

    def __init__(self, message: str, file_path: str = None, original_exception: Exception = None):
        """
        Initialize file operation error.

        Args:
            message: Error message
            file_path: Path to the file that caused the error
            original_exception: Original exception that caused this error
        """
        super().__init__(message, original_exception)
        self.file_path = file_path


class UploadError(MineruException):
    """Raised when file upload fails."""

    def __init__(self, message: str, filename: str = None, original_exception: Exception = None):
        """
        Initialize upload error.

        Args:
            message: Error message
            filename: Name of the file that failed to upload
            original_exception: Original exception that caused this error
        """
        super().__init__(message, original_exception)
        self.filename = filename


class DownloadError(MineruException):
    """Raised when file download fails."""

    def __init__(self, message: str, url: str = None, original_exception: Exception = None):
        """
        Initialize download error.

        Args:
            message: Error message
            url: URL that failed to download
            original_exception: Original exception that caused this error
        """
        super().__init__(message, original_exception)
        self.url = url


class BatchProcessingError(MineruException):
    """Raised when batch processing fails."""

    def __init__(self, message: str, batch_id: str = None, original_exception: Exception = None):
        """
        Initialize batch processing error.

        Args:
            message: Error message
            batch_id: ID of the batch that failed
            original_exception: Original exception that caused this error
        """
        super().__init__(message, original_exception)
        self.batch_id = batch_id
