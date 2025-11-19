"""MinerU API Client Module.

This module provides the MineruClient class for interacting with the MinerU API.
It handles all API operations including:
    - Secure authentication via bearer token
    - Batch file uploads with parallel processing (up to 5 concurrent)
    - Processing status monitoring
    - Automated result downloads

The client implements robust error handling with custom exceptions for different
failure scenarios, comprehensive input validation, and secure credential storage.

Configuration:
    Settings are loaded from two sources:
        - API token: Stored securely in Linux Keyring (never in plaintext files)
        - Other settings: Stored in config.ini (non-sensitive data)

    See SettingsDialog for user-friendly configuration interface.

Example:
    Basic usage workflow:

    >>> client = MineruClient()
    >>> result = client.upload_batch(['file1.pdf', 'file2.pdf'])
    >>> batch_id = result['batch_id']
    >>>
    >>> status = client.get_batch_status(batch_id)
    >>> if status['data']['extract_result'][0]['state'] == 'done':
    ...     zip_url = status['data']['extract_result'][0]['full_zip_url']
    ...     client.download_result(zip_url, 'result.zip')

Thread Safety:
    MineruClient is NOT thread-safe. Create separate instances for different
    threads, or use locks to protect shared access.

Security Considerations:
    - Tokens stored in system keyring (OS-level encryption)
    - All API communication over HTTPS
    - Sensitive data never logged or printed
    - Input validation prevents injection attacks

For detailed API documentation, see docs/API.md
"""

import configparser
import os
import requests
import keyring
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Optional, Callable
from exceptions import (
    ConfigurationError, AuthenticationError, ValidationError,
    APIError, NetworkError, UploadError, DownloadError
)
from validators import (
    validate_api_token, validate_file_path, validate_directory_path,
    validate_file_format, validate_batch_id, validate_language_code,
    validate_model_version
)


class MineruClient:
    """Client for interacting with the MinerU API.

    This class handles all communication with the MinerU service,
    including file uploads, processing status checks, and result downloads.

    The client implements:
        - Secure token-based authentication (Bearer tokens)
        - Parallel file uploads (up to 5 concurrent via ThreadPoolExecutor)
        - Comprehensive error handling with custom exceptions
        - Automatic configuration loading from keyring and config files
        - Input validation for all parameters

    Attributes:
        CONFIG_FILE (str): Path to configuration file ("config.ini")
        KEYRING_SERVICE (str): Service name for keyring storage ("MinerU")
        KEYRING_USERNAME (str): Username for keyring storage ("api_token")
        API_BASE_URL (str): Base URL for MinerU API
        api_token (Optional[str]): Bearer token for API authentication
        is_ocr (bool): Enable OCR for all documents (default: True)
        enable_formula (bool): Enable formula recognition (default: False)
        enable_table (bool): Enable table recognition (default: True)
        language (str): OCR language code - pt, en, ch (default: "pt")
        model_version (str): Processing model - pipeline or vlm (default: "pipeline")
        output_directory (str): Path for downloaded results

    Thread Safety:
        Not thread-safe. Use separate instances per thread.

    Example:
        >>> client = MineruClient()
        >>> # Upload files
        >>> result = client.upload_batch(['doc.pdf'])
        >>> print(result['batch_id'])
        batch_abc123

        >>> # Check status
        >>> status = client.get_batch_status('batch_abc123')
        >>> print(status['data']['extract_result'][0]['state'])
        done

        >>> # Download result
        >>> client.download_result(url, 'output.zip')
        '/home/user/Documents/MinerU_Output/output.zip'
    """

    CONFIG_FILE = "config.ini"
    KEYRING_SERVICE = "MinerU"
    KEYRING_USERNAME = "api_token"
    API_BASE_URL = "https://mineru.net/api/v4"

    def __init__(self):
        """Initialize the MinerU client with default configuration.

        Loads configuration from keyring and config file. Sets default values
        for processing options if no configuration exists.

        The initialization process:
            1. Set default attribute values
            2. Load API token from system keyring
            3. Load processing options from config.ini
            4. Create output directory if needed

        Default values:
            - is_ocr: True
            - enable_formula: False
            - enable_table: True
            - language: "pt" (Portuguese)
            - model_version: "pipeline"
            - output_directory: ~/Documents/MinerU_Output

        Raises:
            ConfigurationError: If configuration is invalid
            ValidationError: If loaded values fail validation

        Example:
            >>> client = MineruClient()
            >>> # Client ready with default or loaded config
            >>> print(client.language)
            pt
        """
        self.api_token = None
        self.is_ocr = True
        self.enable_formula = False
        self.enable_table = True
        self.language = "pt"
        self.model_version = "pipeline"  # Use 'pipeline' for better Portuguese support
        self.output_directory = os.path.expanduser("~/Documents/MinerU_Output")
        self.load_config()

    def load_config(self):
        """Load configuration from keyring and config file.

        Retrieves API token from system keyring and loads processing options
        from config.ini. Uses default values if configuration doesn't exist.
        Validates all loaded values.

        Configuration loaded:
            - api_token: From keyring (secure storage, OS-encrypted)
            - is_ocr: Force OCR flag (bool)
            - enable_formula: Formula recognition flag (bool)
            - enable_table: Table recognition flag (bool)
            - language: OCR language code (pt, en, ch)
            - model_version: Processing model (pipeline or vlm)
            - output_directory: Path for downloads (created if missing)

        Validation:
            - Tokens must be non-empty strings
            - Language codes must be pt, en, or ch
            - Model version must be pipeline or vlm
            - Output directory must be valid path

        Error Handling:
            - Invalid values trigger warnings and use defaults
            - Keyring access failures print warning but don't fail
            - Missing config.ini is normal, uses built-in defaults

        Raises:
            ValidationError: If critical validation fails
            ConfigurationError: If config file is malformed

        Example:
            >>> client = MineruClient()
            >>> client.language = "en"
            >>> client.save_config()  # Save to file
            >>> client.load_config()  # Reload
            >>> print(client.language)
            en

        Side Effects:
            - May create output_directory on filesystem
            - Prints warnings to console for non-critical issues
        """
        # Load token from keyring (secure storage)
        try:
            token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
            if token:
                self.api_token = validate_api_token(token)
        except ValidationError:
            # Re-raise validation errors
            raise
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

            # Validate language
            language = config["Settings"].get("language", "pt")
            try:
                self.language = validate_language_code(language)
            except ValidationError as e:
                print(f"Warning: Invalid language code '{language}', using default 'pt': {e}")
                self.language = "pt"

            # Validate model version
            model_version = config["Settings"].get("model_version", "pipeline")
            try:
                self.model_version = validate_model_version(model_version)
            except ValidationError as e:
                print(f"Warning: Invalid model version '{model_version}', using default 'pipeline': {e}")
                self.model_version = "pipeline"

        if "Paths" in config:
            output_dir = config["Paths"].get("output_directory", "~/Documents/MinerU_Output")
            try:
                self.output_directory = validate_directory_path(output_dir, create_if_missing=True)
            except ValidationError as e:
                print(f"Warning: Invalid output directory '{output_dir}', using default: {e}")
                self.output_directory = os.path.expanduser("~/Documents/MinerU_Output")

    def get_headers(self) -> Dict[str, str]:
        """Get HTTP headers with authorization token.

        Constructs HTTP headers dictionary including Bearer token authentication.
        Used internally by all API methods.

        Returns:
            dict: Headers including Authorization bearer token
                {
                    "Authorization": "Bearer <token>"
                }

        Raises:
            AuthenticationError: If API token is not configured

        Example:
            >>> client = MineruClient()
            >>> headers = client.get_headers()
            >>> print(headers)
            {'Authorization': 'Bearer abc123...'}

        Note:
            This method does not validate the token, only checks it exists.
            Token validation happens during actual API calls (401/403 errors).
        """
        if not self.api_token:
            raise AuthenticationError("API token not configured. Please set it in Settings.")

        return {
            "Authorization": f"Bearer {self.api_token}"
        }

    def get_processing_options(self) -> Dict[str, any]:
        """Get current processing options for batch-level parameters.

        Returns dictionary of processing configuration for API requests.
        These options apply to the entire batch.

        Note:
            is_ocr is NOT included here as it must be set at the file level
            according to the MinerU API specification (v4).

        Returns:
            dict: Processing configuration options containing:
                - enable_formula (bool): Formula recognition flag
                - enable_table (bool): Table recognition flag
                - model_version (str): Processing model ("pipeline" or "vlm")
                - language (str): OCR language code (only for pipeline model)

        Example:
            >>> client = MineruClient()
            >>> options = client.get_processing_options()
            >>> print(options)
            {
                'enable_formula': False,
                'enable_table': True,
                'model_version': 'pipeline',
                'language': 'pt'
            }

        Language Support:
            - Pipeline model: Supports pt, en, ch
            - VLM model: No language parameter (multilingual)

        Note:
            Language parameter is automatically excluded for VLM model
            as it doesn't support language configuration.
        """
        options = {
            "enable_formula": self.enable_formula,
            "enable_table": self.enable_table,
            "model_version": self.model_version
        }

        # Only include language parameter for pipeline backend
        # (VLM doesn't support language configuration)
        if self.model_version == "pipeline":
            options["language"] = self.language

        return options

    def upload_batch(self, file_paths: List[str], progress_callback: Optional[Callable[[int], None]] = None) -> Dict:
        """Upload a batch of files to MinerU API for processing with parallel uploads.

        This follows a two-step process:
        1. POST request to API to get batch_id and presigned S3 URLs
        2. Parallel PUT requests to upload actual file data to presigned URLs

        Uses ThreadPoolExecutor for parallel uploads (max 5 concurrent).
        Progress callback is invoked after each file completes (not during).

        Args:
            file_paths: List of local file paths to upload. Must be valid paths
                to existing files in supported formats (PDF, DOCX, PPTX, JPG, PNG).
            progress_callback: Optional callback function for progress updates.
                Receives integer 0-100 representing percentage complete.
                Called after each file upload completes.

        Returns:
            dict: Response containing batch_id and upload status:
                {
                    "batch_id": str,  # Unique batch identifier for status checks
                    "uploads": [
                        {
                            "file": str,         # Filename
                            "status": "success" | "failed",
                            "error": str         # Error message (if failed)
                        },
                        ...
                    ]
                }

        Raises:
            ValidationError: If files are invalid (missing, wrong format, etc.)
            AuthenticationError: If API token is not configured or invalid (401/403)
            UploadError: If upload fails (S3 upload errors)
            NetworkError: If network connectivity issues occur
            APIError: If API returns unexpected response

        Example:
            >>> def show_progress(percent):
            ...     print(f"Progress: {percent}%")
            ...
            >>> client = MineruClient()
            >>> result = client.upload_batch(
            ...     ['doc1.pdf', 'doc2.pdf'],
            ...     progress_callback=show_progress
            ... )
            Progress: 50%
            Progress: 100%
            >>> print(result['batch_id'])
            batch_abc123
            >>> for upload in result['uploads']:
            ...     print(f"{upload['file']}: {upload['status']}")
            doc1.pdf: success
            doc2.pdf: success

        Behavior:
            - Validates all files before starting uploads
            - Stops validation on first invalid file
            - Uploads continue even if some fail (partial success allowed)
            - Progress callback receives cumulative percentage
            - File-level is_ocr setting included per API spec

        Performance:
            - Max 5 concurrent uploads via ThreadPoolExecutor
            - Large files may take several minutes
            - No timeout on individual file uploads (300s default)

        Note:
            The batch_id returned is needed for get_batch_status().
            Keep it to monitor processing status.
        """
        if not file_paths:
            raise ValidationError("No files provided for upload")

        # Validate all file paths and formats
        validated_paths = []
        for file_path in file_paths:
            try:
                validated_path = validate_file_path(file_path)
                validate_file_format(validated_path)
                validated_paths.append(validated_path)
            except ValidationError as e:
                raise ValidationError(f"Invalid file '{file_path}': {e}")

        file_paths = validated_paths

        # Step 1: Request batch upload URLs
        api_url = f"{self.API_BASE_URL}/file-urls/batch"

        # Prepare file list
        # Note: is_ocr parameter must be included at the file level, not batch level
        files_list = [{"name": os.path.basename(fp), "is_ocr": self.is_ocr} for fp in file_paths]

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
        except requests.ConnectionError as e:
            raise NetworkError(f"Failed to connect to MinerU API. Please check your internet connection: {e}")
        except requests.Timeout as e:
            raise NetworkError(f"Request to MinerU API timed out. Please try again: {e}")
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Invalid API token. Please check your settings.")
            elif response.status_code == 403:
                raise AuthenticationError("Access forbidden. Please verify your API token permissions.")
            else:
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.text
                )

        response_data = response.json()

        # Extract data from response structure
        data = response_data.get("data", {})
        batch_id = data.get("batch_id")
        file_urls = data.get("file_urls", [])

        if not batch_id or not file_urls:
            raise APIError("Invalid response from API: missing batch_id or file_urls")

        if len(file_urls) != len(file_paths):
            raise APIError(f"URL count mismatch: got {len(file_urls)}, expected {len(file_paths)}")

        # Step 2: Upload files in parallel using ThreadPoolExecutor
        upload_results = []
        total_files = len(file_paths)
        completed_count = 0

        def upload_single_file(file_path: str, upload_url: str) -> Dict:
            """Upload a single file to its presigned URL."""
            try:
                if not upload_url:
                    raise UploadError(f"No upload URL for file: {file_path}")

                # Upload file data
                with open(file_path, 'rb') as f:
                    put_response = requests.put(upload_url, data=f, timeout=300)
                    put_response.raise_for_status()

                return {
                    "file": os.path.basename(file_path),
                    "status": "success"
                }

            except UploadError as e:
                return {
                    "file": os.path.basename(file_path),
                    "status": "failed",
                    "error": str(e)
                }
            except Exception as e:
                return {
                    "file": os.path.basename(file_path),
                    "status": "failed",
                    "error": f"Upload failed: {str(e)}"
                }

        # Use ThreadPoolExecutor for parallel uploads (max 5 concurrent uploads)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_file = {
                executor.submit(upload_single_file, file_path, upload_url): file_path
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

        return {
            "batch_id": batch_id,
            "uploads": upload_results
        }

    def get_batch_status(self, batch_id: str) -> Dict:
        """Get the processing status of a batch.

        Queries the MinerU API for the current state of all files in a batch.
        Used for polling to detect completion and obtain download URLs.

        Args:
            batch_id: The batch ID to check (obtained from upload_batch)

        Returns:
            dict: Status information for all files in the batch:
                {
                    "data": {
                        "batch_id": str,
                        "extract_result": [
                            {
                                "file_name": str,        # Original filename
                                "state": str,            # pending/processing/done/failed
                                "err_msg": str,          # Error message (if failed)
                                "full_zip_url": str      # Download URL (if done)
                            },
                            ...
                        ]
                    }
                }

        Raises:
            ValidationError: If batch_id is invalid (empty or wrong format)
            AuthenticationError: If API token is not configured or invalid
            APIError: If batch not found (404) or other API error
            NetworkError: If network connectivity issues occur

        Example:
            >>> client = MineruClient()
            >>> status = client.get_batch_status('batch_abc123')
            >>> for file_info in status['data']['extract_result']:
            ...     print(f"{file_info['file_name']}: {file_info['state']}")
            doc1.pdf: done
            doc2.pdf: processing

        File States:
            - pending: Queued, not yet started
            - processing: Currently being processed
            - done: Complete, ready for download (full_zip_url available)
            - failed: Processing failed (err_msg contains reason)

        Typical Usage:
            Poll this method every 10-30 seconds until all files
            reach 'done' or 'failed' state. Then download completed files.

        Note:
            Response structure matches MinerU API v4 format.
            The full_zip_url is a presigned S3 URL with limited validity.
        """
        # Validate batch_id
        batch_id = validate_batch_id(batch_id)

        api_url = f"{self.API_BASE_URL}/extract-results/batch/{batch_id}"
        headers = self.get_headers()

        try:
            response = requests.get(api_url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.ConnectionError as e:
            raise NetworkError(f"Failed to connect to MinerU API. Please check your internet connection: {e}")
        except requests.Timeout as e:
            raise NetworkError(f"Request to MinerU API timed out. Please try again: {e}")
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise AuthenticationError("Invalid API token. Please check your settings.")
            elif response.status_code == 404:
                raise APIError(f"Batch ID {batch_id} not found.", status_code=404)
            else:
                raise APIError(
                    f"API request failed with status {response.status_code}",
                    status_code=response.status_code,
                    response_data=response.text
                )

    def download_result(self, zip_url: str, filename: str) -> str:
        """Download a result file from the given URL.

        Downloads processed result ZIP file from presigned S3 URL to local
        output directory. Creates output directory if it doesn't exist.

        Args:
            zip_url: URL to download the zip file from (presigned S3 URL
                from get_batch_status full_zip_url field)
            filename: Name for the downloaded file (e.g., "doc1_result.zip")

        Returns:
            str: Full path to the downloaded file
                (e.g., "/home/user/Documents/MinerU_Output/doc1_result.zip")

        Raises:
            ValidationError: If inputs are invalid (empty strings, etc.)
            DownloadError: If download fails or file write fails
            NetworkError: If network connectivity issues occur

        Example:
            >>> client = MineruClient()
            >>> status = client.get_batch_status('batch_abc123')
            >>> file_info = status['data']['extract_result'][0]
            >>> if file_info['state'] == 'done':
            ...     url = file_info['full_zip_url']
            ...     path = client.download_result(url, 'result.zip')
            ...     print(f"Downloaded to: {path}")
            Downloaded to: /home/user/Documents/MinerU_Output/result.zip

        Behavior:
            - Downloads in 8KB chunks (streaming)
            - Creates output_directory if missing
            - Overwrites existing file with same name
            - Validates inputs before starting download

        Performance:
            - Uses streaming download (no memory issues with large files)
            - 300 second timeout per download
            - Chunk size: 8192 bytes

        Side Effects:
            - Creates self.output_directory on filesystem if missing
            - Writes file to disk at output_directory/filename

        Note:
            Presigned URLs have expiration (usually 1 hour).
            Download promptly after getting the URL.
        """
        # Validate inputs
        if not zip_url or not isinstance(zip_url, str):
            raise ValidationError("Download URL must be a non-empty string")

        if not filename or not isinstance(filename, str):
            raise ValidationError("Filename must be a non-empty string")

        # Ensure output directory exists
        try:
            validate_directory_path(self.output_directory, create_if_missing=True)
        except ValidationError as e:
            raise DownloadError(f"Invalid output directory: {e}")

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

        except requests.ConnectionError as e:
            raise NetworkError(f"Failed to download file. Please check your internet connection: {e}")
        except requests.Timeout as e:
            raise NetworkError(f"Download timed out. Please try again: {e}")
        except IOError as e:
            raise DownloadError(f"Failed to write file to disk: {e}")
        except Exception as e:
            raise DownloadError(f"Failed to download file: {str(e)}")
