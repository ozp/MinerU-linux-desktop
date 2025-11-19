"""
MinerU API Client Service.

This module provides a clean interface to the MinerU API,
focusing solely on HTTP communication and response handling.
Business logic is handled by separate service classes.
"""

import os
from typing import Dict, List, Callable, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

from ..config.constants import (
    API_BASE_URL,
    API_TIMEOUT_DEFAULT,
    API_TIMEOUT_UPLOAD,
    API_TIMEOUT_DOWNLOAD,
    MAX_UPLOAD_WORKERS,
    DOWNLOAD_CHUNK_SIZE,
)
from ..config.config_manager import get_config
from ..models.processing_options import ProcessingOptions
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class APIClientError(Exception):
    """Base exception for API client errors."""
    pass


class AuthenticationError(APIClientError):
    """Raised when API authentication fails."""
    pass


class ConnectionError(APIClientError):
    """Raised when connection to API fails."""
    pass


class MineruAPIClient:
    """
    Low-level client for MinerU API communication.

    This class handles all HTTP requests to the MinerU API,
    including authentication, error handling, and response parsing.
    """

    def __init__(self) -> None:
        """Initialize the API client."""
        self.config = get_config()
        logger.info("MinerU API client initialized")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authorization token.

        Returns:
            Dictionary with authorization headers

        Raises:
            AuthenticationError: If API token is not configured
        """
        if not self.config.api_token:
            raise AuthenticationError(
                "API token not configured. Please set it in Settings."
            )

        return {"Authorization": f"Bearer {self.config.api_token}"}

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and check for errors.

        Args:
            response: Response from requests library

        Returns:
            Parsed JSON response

        Raises:
            AuthenticationError: If authentication fails (401/403)
            APIClientError: For other API errors
        """
        try:
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if response.status_code == 401:
                logger.error("Authentication failed: Invalid API token")
                raise AuthenticationError(
                    "Invalid API token. Please check your settings."
                )
            elif response.status_code == 403:
                logger.error("Access forbidden: Insufficient permissions")
                raise AuthenticationError(
                    "Access forbidden. Please verify your API token permissions."
                )
            elif response.status_code == 404:
                logger.error(f"Resource not found: {response.url}")
                raise APIClientError("Resource not found")
            else:
                logger.error(f"API request failed with status {response.status_code}")
                raise APIClientError(
                    f"API request failed with status {response.status_code}: {e}"
                )

    def request_batch_upload_urls(
        self,
        file_paths: List[str],
        processing_options: ProcessingOptions,
    ) -> Dict[str, Any]:
        """
        Request batch upload URLs from the API.

        This is step 1 of the upload process: getting presigned URLs
        and a batch_id for the files.

        Args:
            file_paths: List of local file paths to upload
            processing_options: Processing configuration

        Returns:
            Dictionary with batch_id and file_urls

        Raises:
            ValueError: If no files provided
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            APIClientError: For other API errors
        """
        if not file_paths:
            raise ValueError("No files provided for upload")

        api_url = f"{API_BASE_URL}/file-urls/batch"

        # Prepare file list with file-level parameters
        files_list = [
            {
                "name": os.path.basename(fp),
                **processing_options.to_file_params()
            }
            for fp in file_paths
        ]

        # Prepare request body with batch-level parameters
        request_body = {
            "files": files_list,
            **processing_options.to_batch_params()
        }

        headers = self._get_headers()
        headers["Content-Type"] = "application/json"

        logger.info(f"Requesting batch upload URLs for {len(file_paths)} files")
        logger.debug(f"Request body: {request_body}")

        try:
            response = requests.post(
                api_url,
                json=request_body,
                headers=headers,
                timeout=API_TIMEOUT_DEFAULT
            )
            data = self._handle_response(response)

            logger.info("Successfully received batch upload URLs")
            return data

        except requests.ConnectionError as e:
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(
                "Failed to connect to MinerU API. Please check your internet connection."
            )
        except requests.Timeout as e:
            logger.error(f"Request timed out: {e}")
            raise APIClientError(
                "Request to MinerU API timed out. Please try again."
            )

    def upload_file_to_url(
        self,
        file_path: str,
        upload_url: str
    ) -> Dict[str, str]:
        """
        Upload a single file to a presigned URL.

        Args:
            file_path: Local path to the file
            upload_url: Presigned URL for upload

        Returns:
            Dictionary with upload result (file, status, error)
        """
        filename = os.path.basename(file_path)

        try:
            if not upload_url:
                raise ValueError(f"No upload URL provided for {filename}")

            logger.debug(f"Uploading {filename} to presigned URL")

            with open(file_path, 'rb') as f:
                response = requests.put(
                    upload_url,
                    data=f,
                    timeout=API_TIMEOUT_UPLOAD
                )
                response.raise_for_status()

            logger.info(f"Successfully uploaded {filename}")
            return {
                "file": filename,
                "status": "success"
            }

        except Exception as e:
            logger.error(f"Failed to upload {filename}: {e}")
            return {
                "file": filename,
                "status": "failed",
                "error": str(e)
            }

    def upload_batch(
        self,
        file_paths: List[str],
        file_urls: List[str],
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> List[Dict[str, str]]:
        """
        Upload multiple files in parallel to presigned URLs.

        This is step 2 of the upload process: uploading file data
        to the presigned URLs obtained in step 1.

        Args:
            file_paths: List of local file paths
            file_urls: List of presigned upload URLs
            progress_callback: Optional callback for progress updates (0-100)

        Returns:
            List of upload results for each file

        Raises:
            ValueError: If file_paths and file_urls lengths don't match
        """
        if len(file_urls) != len(file_paths):
            raise ValueError(
                f"URL count mismatch: got {len(file_urls)}, expected {len(file_paths)}"
            )

        upload_results: List[Dict[str, str]] = []
        total_files = len(file_paths)
        completed_count = 0

        logger.info(f"Starting parallel upload of {total_files} files")

        # Use ThreadPoolExecutor for parallel uploads
        with ThreadPoolExecutor(max_workers=MAX_UPLOAD_WORKERS) as executor:
            future_to_file = {
                executor.submit(self.upload_file_to_url, file_path, upload_url): file_path
                for file_path, upload_url in zip(file_paths, file_urls)
            }

            for future in as_completed(future_to_file):
                result = future.result()
                upload_results.append(result)
                completed_count += 1

                # Update progress
                if progress_callback:
                    progress = int((completed_count / total_files) * 100)
                    progress_callback(progress)

        success_count = sum(1 for r in upload_results if r["status"] == "success")
        logger.info(f"Upload completed: {success_count}/{total_files} successful")

        return upload_results

    def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """
        Get the processing status of a batch.

        Args:
            batch_id: The batch ID to check

        Returns:
            Dictionary with batch status information

        Raises:
            AuthenticationError: If authentication fails
            ConnectionError: If connection fails
            APIClientError: For other API errors
        """
        api_url = f"{API_BASE_URL}/extract-results/batch/{batch_id}"
        headers = self._get_headers()

        logger.debug(f"Checking status for batch {batch_id}")

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=API_TIMEOUT_DEFAULT
            )
            data = self._handle_response(response)

            logger.debug(f"Received status for batch {batch_id}")
            return data

        except requests.ConnectionError as e:
            logger.error(f"Connection failed: {e}")
            raise ConnectionError(
                "Failed to connect to MinerU API. Please check your internet connection."
            )
        except requests.Timeout as e:
            logger.error(f"Request timed out: {e}")
            raise APIClientError(
                "Request to MinerU API timed out. Please try again."
            )

    def download_file(
        self,
        url: str,
        output_path: str
    ) -> None:
        """
        Download a file from a URL.

        Args:
            url: URL to download from
            output_path: Local path to save the file

        Raises:
            ConnectionError: If download fails
            APIClientError: For other errors
        """
        logger.info(f"Downloading file to {output_path}")

        try:
            response = requests.get(
                url,
                timeout=API_TIMEOUT_DOWNLOAD,
                stream=True
            )
            response.raise_for_status()

            # Download in chunks
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Successfully downloaded file to {output_path}")

        except requests.ConnectionError as e:
            logger.error(f"Download connection failed: {e}")
            raise ConnectionError(
                "Failed to download file. Please check your internet connection."
            )
        except requests.Timeout as e:
            logger.error(f"Download timed out: {e}")
            raise APIClientError("Download timed out. Please try again.")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise APIClientError(f"Failed to download file: {str(e)}")
