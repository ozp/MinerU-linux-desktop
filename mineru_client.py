"""
MinerU API Client Module

This module provides the MineruClient class for interacting with the MinerU API.
Handles all API operations including authentication, file upload, status checking,
and result downloads.
"""

import configparser
import os
import requests
import keyring
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable


class MineruClient:
    """
    Client for interacting with the MinerU API.

    This class handles all communication with the MinerU service,
    including file uploads, processing status checks, and result downloads.
    """

    CONFIG_FILE = "config.ini"
    KEYRING_SERVICE = "MinerU"
    KEYRING_USERNAME = "api_token"
    API_BASE_URL = "https://mineru.net/api/v4"

    def __init__(self):
        """Initialize the MinerU client."""
        self.api_token = None
        self.is_ocr = True
        self.enable_formula = False
        self.enable_table = True
        self.language = "pt"
        self.output_directory = os.path.expanduser("~/Documents/MinerU_Output")
        self.load_config()

    def load_config(self):
        """Load configuration from keyring and config file."""
        # Load token from keyring (secure storage)
        try:
            self.api_token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
        except Exception as e:
            print(f"Warning: Could not load token from keyring: {e}")

        # Load non-sensitive settings from config.ini
        if not os.path.exists(self.CONFIG_FILE):
            return

        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE)

        if "Settings" in config:
            self.is_ocr = config["Settings"].getboolean("is_ocr", True)
            self.enable_formula = config["Settings"].getboolean("enable_formula", False)
            self.enable_table = config["Settings"].getboolean("enable_table", True)
            self.language = config["Settings"].get("language", "pt")

        if "Paths" in config:
            output_dir = config["Paths"].get("output_directory", "~/Documents/MinerU_Output")
            self.output_directory = os.path.expanduser(output_dir)

    def get_headers(self) -> Dict[str, str]:
        """
        Get HTTP headers with authorization token.

        Returns:
            dict: Headers including Authorization bearer token

        Raises:
            ValueError: If API token is not configured
        """
        if not self.api_token:
            raise ValueError("API token not configured. Please set it in Settings.")

        return {
            "Authorization": f"Bearer {self.api_token}"
        }

    def get_processing_options(self) -> Dict[str, any]:
        """
        Get current processing options.

        Returns:
            dict: Processing configuration options
        """
        return {
            "is_ocr": self.is_ocr,
            "enable_formula": self.enable_formula,
            "enable_table": self.enable_table,
            "language": self.language
        }

    def upload_batch(self, file_paths: List[str], progress_callback: Optional[Callable[[int], None]] = None) -> Dict:
        """
        Upload a batch of files to MinerU API for processing with parallel uploads.

        This follows a two-step process:
        1. POST request to get batch_id and presigned URLs
        2. Parallel PUT requests to upload actual file data to the presigned URLs

        Args:
            file_paths: List of local file paths to upload
            progress_callback: Optional callback function for progress updates (0-100)

        Returns:
            dict: Response containing batch_id and upload status

        Raises:
            ValueError: If API token is not configured or no files provided
            requests.RequestException: If API request fails
        """
        if not file_paths:
            raise ValueError("No files provided for upload")

        # Step 1: Request batch upload URLs
        api_url = f"{self.API_BASE_URL}/file-urls/batch"

        # Prepare file list
        files_list = [{"name": os.path.basename(fp)} for fp in file_paths]

        # Prepare request body with files and processing options
        request_body = {
            "files": files_list,
            **self.get_processing_options()
        }

        # Make POST request to get batch_id and upload URLs
        headers = self.get_headers()
        headers["Content-Type"] = "application/json"

        try:
            response = requests.post(api_url, json=request_body, headers=headers, timeout=30)
            response.raise_for_status()
        except requests.ConnectionError:
            raise ConnectionError("Failed to connect to MinerU API. Please check your internet connection.")
        except requests.Timeout:
            raise TimeoutError("Request to MinerU API timed out. Please try again.")
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Invalid API token. Please check your settings.")
            elif response.status_code == 403:
                raise ValueError("Access forbidden. Please verify your API token permissions.")
            else:
                raise Exception(f"API request failed with status {response.status_code}: {e}")

        response_data = response.json()
        batch_id = response_data.get("batch_id")
        file_urls = response_data.get("file_urls", [])

        if not batch_id or not file_urls:
            raise ValueError("Invalid response from API: missing batch_id or file_urls")

        if len(file_urls) != len(file_paths):
            raise ValueError(f"URL count mismatch: got {len(file_urls)}, expected {len(file_paths)}")

        # Step 2: Upload files in parallel using ThreadPoolExecutor
        upload_results = []
        total_files = len(file_paths)
        completed_count = 0

        def upload_single_file(file_path: str, url_info: Dict) -> Dict:
            """Upload a single file to its presigned URL."""
            try:
                upload_url = url_info.get("url")
                if not upload_url:
                    raise ValueError(f"No upload URL for file: {file_path}")

                # Upload file data
                with open(file_path, 'rb') as f:
                    put_response = requests.put(upload_url, data=f, timeout=300)
                    put_response.raise_for_status()

                return {
                    "file": os.path.basename(file_path),
                    "status": "success"
                }

            except Exception as e:
                return {
                    "file": os.path.basename(file_path),
                    "status": "failed",
                    "error": str(e)
                }

        # Use ThreadPoolExecutor for parallel uploads (max 5 concurrent uploads)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {
                executor.submit(upload_single_file, file_path, url_info): file_path
                for file_path, url_info in zip(file_paths, file_urls)
            }

            for future in as_completed(future_to_file):
                result = future.result()
                upload_results.append(result)
                completed_count += 1

                # Update progress
                if progress_callback:
                    progress = int((completed_count / total_files) * 100)
                    progress_callback(progress)

        return {
            "batch_id": batch_id,
            "uploads": upload_results
        }

    def get_batch_status(self, batch_id: str) -> Dict:
        """
        Get the processing status of a batch.

        Args:
            batch_id: The batch ID to check

        Returns:
            dict: Status information for all files in the batch

        Raises:
            ValueError: If API token is not configured
            requests.RequestException: If API request fails
        """
        api_url = f"{self.API_BASE_URL}/extract-results/batch/{batch_id}"
        headers = self.get_headers()

        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError:
            raise ConnectionError("Failed to connect to MinerU API. Please check your internet connection.")
        except requests.Timeout:
            raise TimeoutError("Request to MinerU API timed out. Please try again.")
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Invalid API token. Please check your settings.")
            elif response.status_code == 404:
                raise ValueError(f"Batch ID {batch_id} not found.")
            else:
                raise Exception(f"API request failed with status {response.status_code}: {e}")

    def download_result(self, zip_url: str, filename: str) -> str:
        """
        Download a result file from the given URL.

        Args:
            zip_url: URL to download the zip file from
            filename: Name for the downloaded file

        Returns:
            str: Path to the downloaded file

        Raises:
            requests.RequestException: If download fails
        """
        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)

        # Create full output path
        output_path = os.path.join(self.output_directory, filename)

        try:
            response = requests.get(zip_url, timeout=300, stream=True)
            response.raise_for_status()

            # Download file in chunks
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            return output_path

        except requests.ConnectionError:
            raise ConnectionError("Failed to download file. Please check your internet connection.")
        except requests.Timeout:
            raise TimeoutError("Download timed out. Please try again.")
        except Exception as e:
            raise Exception(f"Failed to download file: {str(e)}")
