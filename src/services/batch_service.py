"""
Batch Processing Service.

This module contains the business logic for batch operations,
including upload orchestration, status checking, and result downloading.
This replaces the complex check_batch_status() method from the original code.
"""

import os
import zipfile
from typing import List, Optional, Callable
from pathlib import Path

from .api_client import MineruAPIClient
from ..models.batch import BatchInfo, FileInfo
from ..models.processing_options import ProcessingOptions
from ..config.constants import FileState, FileStatusLocal
from ..config.config_manager import get_config
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class BatchService:
    """
    Service for managing batch upload and processing operations.

    This class orchestrates the entire batch workflow:
    1. Upload batch to API
    2. Poll for processing status
    3. Download and extract results
    """

    def __init__(self, api_client: Optional[MineruAPIClient] = None) -> None:
        """
        Initialize the batch service.

        Args:
            api_client: Optional API client (creates new one if not provided)
        """
        self.api_client = api_client or MineruAPIClient()
        self.config = get_config()
        logger.info("Batch service initialized")

    def create_batch(self, file_paths: List[str]) -> BatchInfo:
        """
        Create a new batch from file paths.

        Args:
            file_paths: List of local file paths

        Returns:
            New BatchInfo instance
        """
        batch = BatchInfo()
        for file_path in file_paths:
            batch.add_file(file_path)

        logger.info(f"Created batch with {len(file_paths)} files")
        return batch

    def upload_batch(
        self,
        batch: BatchInfo,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Upload a batch of files to the API.

        This method performs the two-step upload process:
        1. Request presigned URLs from API
        2. Upload files to presigned URLs

        Args:
            batch: BatchInfo instance with files to upload
            progress_callback: Optional callback for progress updates (0-100)

        Raises:
            Various exceptions from API client
        """
        file_paths = [f.file_path for f in batch.files]
        processing_options = self.config.processing_options

        logger.info(f"Starting upload for batch with {len(file_paths)} files")

        # Step 1: Request batch upload URLs
        response_data = self.api_client.request_batch_upload_urls(
            file_paths,
            processing_options
        )

        # Extract batch_id and file_urls
        data = response_data.get("data", {})
        batch.batch_id = data.get("batch_id")
        file_urls = data.get("file_urls", [])

        if not batch.batch_id:
            raise ValueError("No batch_id received from API")

        logger.info(f"Received batch_id: {batch.batch_id}")

        # Step 2: Upload files in parallel
        upload_results = self.api_client.upload_batch(
            file_paths,
            file_urls,
            progress_callback
        )

        # Store upload results and update file statuses
        batch.upload_results = upload_results

        for result in upload_results:
            filename = result["file"]
            file_info = batch.get_file_by_name(filename)

            if file_info:
                if result["status"] == "success":
                    file_info.status_local = FileStatusLocal.PROCESSING
                    logger.debug(f"File {filename} uploaded successfully")
                else:
                    file_info.status_local = FileStatusLocal.FAILED
                    file_info.error_message = result.get("error", "Upload failed")
                    logger.warning(f"File {filename} upload failed: {file_info.error_message}")

        success_count = batch.get_success_count()
        logger.info(f"Upload completed: {success_count}/{len(file_paths)} successful")

    def check_batch_status(self, batch: BatchInfo) -> bool:
        """
        Check the processing status of a batch and update file information.

        This method replaces the original 127-line check_batch_status() method
        by breaking it down into smaller, focused methods.

        Args:
            batch: BatchInfo instance to check

        Returns:
            True if all files are in final state, False otherwise
        """
        if not batch.batch_id:
            logger.error("No batch_id available for status check")
            return False

        try:
            # Get status from API
            status_data = self.api_client.get_batch_status(batch.batch_id)

            # Extract file information
            data = status_data.get("data", {})
            files_info = data.get("extract_result", [])

            logger.debug(f"Checking batch {batch.batch_id}: {len(files_info)} files in response")

            # Update each file's status
            for file_info in batch.files:
                if file_info.is_final_state():
                    continue  # Skip files already complete

                # Find file in API response
                api_file_data = self._find_file_in_api_response(
                    file_info.filename,
                    files_info
                )

                if api_file_data:
                    self._update_file_from_api(file_info, api_file_data)
                else:
                    logger.debug(f"File {file_info.filename} not yet in API response")

            # Check if all files are complete
            all_done = batch.all_files_complete()

            if all_done:
                logger.info(f"Batch {batch.batch_id} completed: "
                          f"{batch.get_success_count()} succeeded, "
                          f"{batch.get_failed_count()} failed")
            else:
                in_progress = len(batch.get_files_in_progress())
                logger.debug(f"Batch {batch.batch_id}: {in_progress} files still processing")

            return all_done

        except Exception as e:
            logger.error(f"Error checking batch status: {e}", exc_info=True)
            # Don't stop polling on errors
            return False

    def _find_file_in_api_response(
        self,
        filename: str,
        files_info: List[dict]
    ) -> Optional[dict]:
        """
        Find a file in the API response by filename.

        Args:
            filename: Name of the file to find
            files_info: List of file info from API response

        Returns:
            File data dictionary if found, None otherwise
        """
        for file_data in files_info:
            if file_data.get("file_name") == filename:
                return file_data
        return None

    def _update_file_from_api(
        self,
        file_info: FileInfo,
        api_data: dict
    ) -> None:
        """
        Update FileInfo from API response data.

        Args:
            file_info: FileInfo instance to update
            api_data: Dictionary from API extract_result
        """
        # Update file state from API
        file_info.update_from_api(api_data)

        state_str = api_data.get("state", "pending")
        logger.debug(f"File {file_info.filename}: state={state_str}")

        # Handle different states
        if file_info.state == FileState.DONE:
            self._handle_completed_file(file_info)
        elif file_info.state == FileState.FAILED:
            self._handle_failed_file(file_info)
        elif file_info.state in [FileState.PROCESSING, FileState.PENDING]:
            # Keep current status
            file_info.status_local = FileStatusLocal.PROCESSING

    def _handle_completed_file(self, file_info: FileInfo) -> None:
        """
        Handle a file that has completed processing.

        Downloads and extracts the result ZIP file.

        Args:
            file_info: FileInfo instance for completed file
        """
        # Only download if not already downloaded
        if file_info.status_local == FileStatusLocal.COMPLETED:
            return

        if not file_info.zip_url:
            logger.error(f"No zip_url available for {file_info.filename}")
            file_info.status_local = FileStatusLocal.DOWNLOAD_FAILED
            file_info.error_message = "No download URL available"
            return

        try:
            logger.info(f"Downloading result for {file_info.filename}")

            # Download ZIP file
            self._download_and_extract_result(file_info)

            # Update status
            file_info.status_local = FileStatusLocal.COMPLETED
            logger.info(f"Successfully processed {file_info.filename}")

        except Exception as e:
            logger.error(f"Error downloading {file_info.filename}: {e}", exc_info=True)
            file_info.status_local = FileStatusLocal.DOWNLOAD_FAILED
            file_info.error_message = str(e)

    def _handle_failed_file(self, file_info: FileInfo) -> None:
        """
        Handle a file that failed processing.

        Args:
            file_info: FileInfo instance for failed file
        """
        file_info.status_local = FileStatusLocal.FAILED
        logger.warning(f"File {file_info.filename} failed: {file_info.error_message}")

    def _download_and_extract_result(self, file_info: FileInfo) -> None:
        """
        Download and extract result ZIP for a file.

        Args:
            file_info: FileInfo instance with zip_url

        Raises:
            Various exceptions from download or extraction
        """
        # Ensure output directory exists
        self.config.ensure_output_directory_exists()

        # Create temporary ZIP path
        output_filename = f"{os.path.splitext(file_info.filename)[0]}_result.zip"
        zip_path = os.path.join(self.config.output_directory, output_filename)

        # Download ZIP file
        self.api_client.download_file(file_info.zip_url, zip_path)

        # Extract to dedicated folder
        extract_folder = os.path.join(
            self.config.output_directory,
            os.path.splitext(file_info.filename)[0]
        )
        Path(extract_folder).mkdir(parents=True, exist_ok=True)

        logger.debug(f"Extracting {zip_path} to {extract_folder}")

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        # Remove the ZIP file after extraction
        os.remove(zip_path)
        logger.debug(f"Cleaned up temporary ZIP file: {zip_path}")

    def get_batch_summary(self, batch: BatchInfo) -> dict:
        """
        Get a summary of the batch status.

        Args:
            batch: BatchInfo instance

        Returns:
            Dictionary with summary statistics
        """
        total = len(batch.files)
        completed = batch.get_success_count()
        failed = batch.get_failed_count()
        in_progress = len(batch.get_files_in_progress())

        return {
            "total": total,
            "completed": completed,
            "failed": failed,
            "in_progress": in_progress,
            "is_complete": batch.all_files_complete(),
        }
