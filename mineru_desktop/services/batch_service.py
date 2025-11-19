"""
Batch service module.

Handles batch status checking and coordination between upload and download services.
"""

import os
import zipfile
from typing import Dict, List, Optional
from datetime import datetime

from mineru_desktop.core.client import MineruClient
from mineru_desktop.models.batch import Batch, FileState
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class BatchService:
    """Service for managing batch operations."""

    def __init__(self, client: MineruClient, output_directory: str):
        """
        Initialize batch service.

        Args:
            client: MinerU API client
            output_directory: Directory for downloaded results
        """
        self.client = client
        self.output_directory = output_directory
        logger.debug(f"BatchService initialized with output_dir: {output_directory}")

    def check_batch_status(self, batch: Batch) -> Dict[str, any]:
        """
        Check the status of a batch and update file states.

        Args:
            batch: Batch object to check

        Returns:
            Dictionary with status summary:
                - all_done: bool
                - has_completed: bool
                - processing_count: int
                - completed_count: int
                - failed_count: int

        Raises:
            ValueError: If batch_id is not set
            Exception: If API request fails
        """
        if not batch.batch_id:
            logger.error("Batch ID not set")
            raise ValueError("Batch ID not set")

        logger.info(f"Checking batch status: {batch.batch_id}")

        try:
            status_data = self.client.get_batch_status(batch.batch_id)

            # Extract file information from API response
            data = status_data.get("data", {})
            files_info = data.get("extract_result", [])

            logger.debug(f"Found {len(files_info)} files in API response")

            # Create map for quick lookup
            api_files_map = {f.get("file_name"): f for f in files_info}

            all_done = True
            has_completed = False
            files_still_processing = 0

            # Update each file status
            for file_status in batch.files:
                # Skip files already in final state
                if file_status.is_final_state():
                    continue

                filename = file_status.filename

                # Check if file is in API response
                if filename not in api_files_map:
                    logger.debug(f"File {filename} not yet in API response")
                    all_done = False
                    files_still_processing += 1
                    continue

                file_info = api_files_map[filename]
                state = file_info.get("state")
                logger.debug(f"File: {filename}, State: {state}")

                # Update file state based on API response
                if state == "done":
                    # Download and extract the result
                    if self._download_and_extract_file(file_status, file_info):
                        has_completed = True
                    else:
                        all_done = False

                elif state == "failed":
                    err_msg = file_info.get("err_msg", "Unknown error")
                    logger.warning(f"File {filename} failed: {err_msg}")
                    file_status.state = FileState.FAILED
                    file_status.error_message = err_msg

                elif state in ["processing", "pending"]:
                    logger.debug(f"File {filename} still {state}")
                    all_done = False
                    files_still_processing += 1
                    file_status.state = FileState(state)

                else:
                    logger.warning(f"Unknown state '{state}' for {filename}")
                    all_done = False
                    files_still_processing += 1

            # Update batch completion time if all done
            if all_done and not batch.completed_at:
                batch.completed_at = datetime.now()

            summary = {
                "all_done": all_done,
                "has_completed": has_completed,
                "processing_count": files_still_processing,
                "completed_count": batch.get_success_count(),
                "failed_count": batch.get_failed_count()
            }

            logger.info(f"Batch status summary: {summary}")
            return summary

        except Exception as e:
            logger.error(f"Error checking batch status: {e}", exc_info=True)
            raise

    def _download_and_extract_file(
        self,
        file_status,
        file_info: Dict
    ) -> bool:
        """
        Download and extract a completed file.

        Args:
            file_status: FileStatus object
            file_info: File information from API

        Returns:
            True if successful, False otherwise
        """
        filename = file_status.filename

        try:
            zip_url = file_info.get("full_zip_url")
            if not zip_url:
                logger.error(f"No zip_url for {filename}")
                file_status.state = FileState.DOWNLOAD_FAILED
                file_status.error_message = "URL não encontrada"
                return False

            logger.info(f"Downloading result for {filename}")

            # Download ZIP file
            output_filename = f"{os.path.splitext(filename)[0]}_result.zip"
            zip_path = os.path.join(self.output_directory, output_filename)
            self.client.download_result(zip_url, zip_path)

            # Extract ZIP to folder
            extract_folder = os.path.join(
                self.output_directory,
                os.path.splitext(filename)[0]
            )
            os.makedirs(extract_folder, exist_ok=True)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)

            # Remove the ZIP file after extraction
            os.remove(zip_path)

            # Update file status
            file_status.state = FileState.COMPLETED
            file_status.completed_at = datetime.now()
            file_status.download_url = zip_url

            logger.info(f"Successfully downloaded and extracted {filename}")
            return True

        except Exception as e:
            logger.error(f"Error downloading {filename}: {e}", exc_info=True)
            file_status.state = FileState.DOWNLOAD_FAILED
            file_status.error_message = str(e)
            return False
