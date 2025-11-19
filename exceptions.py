"""
Custom exceptions for MinerU Desktop Client.

This module defines custom exception classes to provide more specific error handling
throughout the application.
"""


class MinerUException(Exception):
    """Base exception for all MinerU-related errors."""
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
    """Raised when an API request fails."""

    def __init__(self, message, status_code=None, response_data=None):
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
