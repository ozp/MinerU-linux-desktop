"""
MinerU API Client Module.

Provides the MineruClient class for interacting with the MinerU API.
Handles all API operations including authentication, file upload, status checking,
and result downloads.
"""

import os
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable

from mineru_desktop.models.batch import ProcessingOptions
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class MineruClient:
    """
    Client for interacting with the MinerU API.

    This class handles all communication with the MinerU service,
    including file uploads, processing status checks, and result downloads.
    """

    API_BASE_URL = "https://mineru.net/api/v4"
    MAX_CONCURRENT_UPLOADS = 5
    REQUEST_TIMEOUT = 30
    UPLOAD_TIMEOUT = 300

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the MinerU client.

        Args:
            api_token: Optional API token (can be set later)
        """
        self.api_token = api_token
        logger.info("MineruClient initialized")

    def set_api_token(self, token: str) -> None:
        """
        Set the API token.

        Args:
            token: API authentication token
        """
        self.api_token = token
        logger.debug("API token updated")

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authorization token.

        Returns:
            Dictionary with authorization headers

        Raises:
            ValueError: If API token is not configured
        """
        if not self.api_token:
            logger.error("API token not configured")
            raise ValueError("API token not configured. Please set it in Settings.")

        return {"Authorization": f"Bearer {self.api_token}"}

    def upload_batch(
        self,
        file_paths: List[str],
        processing_options: ProcessingOptions,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> Dict:
        """
        Upload a batch of files to MinerU API for processing with parallel uploads.

        This follows a two-step process:
        1. POST request to get batch_id and presigned URLs
        2. Parallel PUT requests to upload actual file data to the presigned URLs

        Args:
            file_paths: List of local file paths to upload
            processing_options: Processing configuration options
            progress_callback: Optional callback function for progress updates (0-100)

        Returns:
            Dictionary containing batch_id and upload status

        Raises:
            ValueError: If API token is not configured or no files provided
            requests.RequestException: If API request fails
        """
        if not file_paths:
            logger.error("No files provided for upload")
            raise ValueError("No files provided for upload")

        logger.info(f"Starting batch upload of {len(file_paths)} files")

        # Step 1: Request batch upload URLs
        api_url = f"{self.API_BASE_URL}/file-urls/batch"

        # Prepare file list with is_ocr parameter at file level
        files_list = [
            {"name": os.path.basename(fp), "is_ocr": processing_options.is_ocr}
            for fp in file_paths
        ]

        # Prepare request body
        request_body = {
            "files": files_list,
            **processing_options.to_dict()
        }

        logger.debug(f"Request body: {request_body}")

        # Make POST request to get batch_id and upload URLs
        headers = self.get_headers()
        headers["Content-Type"] = "application/json"

        try:
            response = requests.post(
                api_url,
                json=request_body,
                headers=headers,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            logger.info("Batch upload URLs received successfully")

        except requests.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            raise ConnectionError(
                "Failed to connect to MinerU API. Please check your internet connection."
            )
        except requests.Timeout as e:
            logger.error(f"Request timeout: {e}")
            raise TimeoutError("Request to MinerU API timed out. Please try again.")
        except requests.HTTPError as e:
            if response.status_code == 401:
                logger.error("Authentication failed (401)")
                raise ValueError("Invalid API token. Please check your settings.")
            elif response.status_code == 403:
                logger.error("Access forbidden (403)")
                raise ValueError("Access forbidden. Please verify your API token permissions.")
            else:
                logger.error(f"HTTP error {response.status_code}: {e}")
                raise Exception(f"API request failed with status {response.status_code}: {e}")

        response_data = response.json()

        # Extract data from response structure
        data = response_data.get("data", {})
        batch_id = data.get("batch_id")
        file_urls = data.get("file_urls", [])

        if not batch_id or not file_urls:
            logger.error("Invalid API response: missing batch_id or file_urls")
            raise ValueError("Invalid response from API: missing batch_id or file_urls")

        if len(file_urls) != len(file_paths):
            logger.error(f"URL count mismatch: got {len(file_urls)}, expected {len(file_paths)}")
            raise ValueError(
                f"URL count mismatch: got {len(file_urls)}, expected {len(file_paths)}"
            )

        logger.info(f"Batch ID: {batch_id}")

        # Step 2: Upload files in parallel
        upload_results = self._upload_files_parallel(
            file_paths,
            file_urls,
            progress_callback
        )

        success_count = sum(1 for r in upload_results if r["status"] == "success")
        logger.info(f"Upload completed: {success_count}/{len(file_paths)} successful")

        return {
            "batch_id": batch_id,
            "uploads": upload_results
        }

    def _upload_files_parallel(
        self,
        file_paths: List[str],
        upload_urls: List[str],
        progress_callback: Optional[Callable[[int], None]]
    ) -> List[Dict]:
        """
        Upload files in parallel using ThreadPoolExecutor.

        Args:
            file_paths: List of file paths to upload
            upload_urls: List of presigned upload URLs
            progress_callback: Optional progress callback

        Returns:
            List of upload results
        """
        upload_results = []
        total_files = len(file_paths)
        completed_count = 0

        def upload_single_file(file_path: str, upload_url: str) -> Dict:
            """Upload a single file to its presigned URL."""
            try:
                if not upload_url:
                    raise ValueError(f"No upload URL for file: {file_path}")

                logger.debug(f"Uploading: {os.path.basename(file_path)}")

                with open(file_path, 'rb') as f:
                    put_response = requests.put(
                        upload_url,
                        data=f,
                        timeout=self.UPLOAD_TIMEOUT
                    )
                    put_response.raise_for_status()

                logger.info(f"Successfully uploaded: {os.path.basename(file_path)}")
                return {
                    "file": os.path.basename(file_path),
                    "status": "success"
                }

            except Exception as e:
                logger.error(f"Upload failed for {os.path.basename(file_path)}: {e}")
                return {
                    "file": os.path.basename(file_path),
                    "status": "failed",
                    "error": str(e)
                }

        # Use ThreadPoolExecutor for parallel uploads
        with ThreadPoolExecutor(max_workers=self.MAX_CONCURRENT_UPLOADS) as executor:
            future_to_file = {
                executor.submit(upload_single_file, file_path, upload_url): file_path
                for file_path, upload_url in zip(file_paths, upload_urls)
            }

            for future in as_completed(future_to_file):
                result = future.result()
                upload_results.append(result)
                completed_count += 1

                # Update progress
                if progress_callback:
                    progress = int((completed_count / total_files) * 100)
                    progress_callback(progress)

        return upload_results

    def get_batch_status(self, batch_id: str) -> Dict:
        """
        Get the processing status of a batch.

        Args:
            batch_id: The batch ID to check

        Returns:
            Dictionary with status information for all files in the batch

        Raises:
            ValueError: If API token is not configured
            requests.RequestException: If API request fails
        """
        logger.debug(f"Checking status for batch: {batch_id}")

        api_url = f"{self.API_BASE_URL}/extract-results/batch/{batch_id}"
        headers = self.get_headers()

        try:
            response = requests.get(
                api_url,
                headers=headers,
                timeout=self.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            logger.debug(f"Status check successful for batch: {batch_id}")
            return response.json()

        except requests.ConnectionError as e:
            logger.error(f"Connection error during status check: {e}")
            raise ConnectionError(
                "Failed to connect to MinerU API. Please check your internet connection."
            )
        except requests.Timeout as e:
            logger.error(f"Timeout during status check: {e}")
            raise TimeoutError("Request to MinerU API timed out. Please try again.")
        except requests.HTTPError as e:
            if response.status_code == 401:
                logger.error("Authentication failed during status check (401)")
                raise ValueError("Invalid API token. Please check your settings.")
            elif response.status_code == 404:
                logger.error(f"Batch not found: {batch_id}")
                raise ValueError(f"Batch ID {batch_id} not found.")
            else:
                logger.error(f"HTTP error during status check {response.status_code}: {e}")
                raise Exception(f"API request failed with status {response.status_code}: {e}")

    def download_result(self, zip_url: str, output_path: str) -> str:
        """
        Download a result file from the given URL.

        Args:
            zip_url: URL to download the zip file from
            output_path: Full path where to save the downloaded file

        Returns:
            Path to the downloaded file

        Raises:
            requests.RequestException: If download fails
        """
        logger.info(f"Downloading result to: {output_path}")

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            response = requests.get(zip_url, timeout=self.UPLOAD_TIMEOUT, stream=True)
            response.raise_for_status()

            # Download file in chunks
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            logger.info(f"Download completed: {output_path}")
            return output_path

        except requests.ConnectionError as e:
            logger.error(f"Connection error during download: {e}")
            raise ConnectionError(
                "Failed to download file. Please check your internet connection."
            )
        except requests.Timeout as e:
            logger.error(f"Timeout during download: {e}")
            raise TimeoutError("Download timed out. Please try again.")
        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise Exception(f"Failed to download file: {str(e)}")
