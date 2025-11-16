"""
MinerU API Client Module

This module provides the MineruClient class for interacting with the MinerU API.
Handles all API operations including authentication, file upload, status checking,
and result downloads.
"""

import configparser
import os
import requests


class MineruClient:
    """
    Client for interacting with the MinerU API.

    This class handles all communication with the MinerU service,
    including file uploads, processing status checks, and result downloads.
    """

    CONFIG_FILE = "config.ini"

    def __init__(self):
        """Initialize the MinerU client."""
        self.api_token = None
        self.is_ocr = False
        self.enable_formula = False
        self.enable_table = False
        self.language = "en"
        self.load_config()

    def load_config(self):
        """Load configuration from config.ini file."""
        if not os.path.exists(self.CONFIG_FILE):
            return

        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE)

        if "API" in config:
            self.api_token = config["API"].get("token", "")

        if "Processing" in config:
            self.is_ocr = config["Processing"].getboolean("is_ocr", False)
            self.enable_formula = config["Processing"].getboolean("enable_formula", False)
            self.enable_table = config["Processing"].getboolean("enable_table", False)
            self.language = config["Processing"].get("language", "en")

    def get_headers(self):
        """
        Get HTTP headers with authorization token.

        Returns:
            dict: Headers including Authorization bearer token
        """
        if not self.api_token:
            raise ValueError("API token not configured. Please set it in Settings.")

        return {
            "Authorization": f"Bearer {self.api_token}"
        }

    def get_processing_options(self):
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

    def upload_batch(self, file_paths):
        """
        Upload a batch of files to MinerU API for processing.

        This follows a two-step process:
        1. POST request to get batch_id and presigned URLs
        2. PUT requests to upload actual file data to the presigned URLs

        Args:
            file_paths (list): List of local file paths to upload

        Returns:
            dict: Response containing batch_id and upload status

        Raises:
            ValueError: If API token is not configured
            requests.RequestException: If API request fails
        """
        if not file_paths:
            raise ValueError("No files provided for upload")

        # Step 1: Request batch upload URLs
        api_url = "https://mineru.net/api/v4/file-urls/batch"

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

        response = requests.post(api_url, json=request_body, headers=headers)
        response.raise_for_status()

        response_data = response.json()
        batch_id = response_data.get("batch_id")
        file_urls = response_data.get("file_urls", [])

        if not batch_id or not file_urls:
            raise ValueError("Invalid response from API: missing batch_id or file_urls")

        if len(file_urls) != len(file_paths):
            raise ValueError(f"URL count mismatch: got {len(file_urls)}, expected {len(file_paths)}")

        # Step 2: Upload each file to its presigned URL
        upload_results = []
        for i, (file_path, url_info) in enumerate(zip(file_paths, file_urls)):
            try:
                upload_url = url_info.get("url")
                if not upload_url:
                    raise ValueError(f"No upload URL for file: {file_path}")

                # Upload file data
                with open(file_path, 'rb') as f:
                    put_response = requests.put(upload_url, data=f)
                    put_response.raise_for_status()

                upload_results.append({
                    "file": os.path.basename(file_path),
                    "status": "success"
                })

            except Exception as e:
                upload_results.append({
                    "file": os.path.basename(file_path),
                    "status": "failed",
                    "error": str(e)
                })

        return {
            "batch_id": batch_id,
            "uploads": upload_results
        }
