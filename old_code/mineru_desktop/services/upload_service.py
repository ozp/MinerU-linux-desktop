"""
Upload service module.

Handles file upload operations.
"""

from typing import List, Optional, Callable

from mineru_desktop.core.client import MineruClient
from mineru_desktop.models.batch import Batch, FileState, ProcessingOptions
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class UploadService:
    """Service for handling file uploads."""

    def __init__(self, client: MineruClient):
        """
        Initialize upload service.

        Args:
            client: MinerU API client
        """
        self.client = client
        logger.debug("UploadService initialized")

    def upload_batch(
        self,
        batch: Batch,
        progress_callback: Optional[Callable[[int], None]] = None
    ) -> None:
        """
        Upload all files in a batch.

        Args:
            batch: Batch object containing files to upload
            progress_callback: Optional progress callback (0-100)

        Raises:
            ValueError: If no files in batch
            Exception: If upload fails
        """
        if not batch.files:
            logger.error("No files in batch to upload")
            raise ValueError("No files in batch")

        file_paths = [f.file_path for f in batch.files]
        logger.info(f"Uploading batch with {len(file_paths)} files")

        # Update all files to uploading state
        for file_status in batch.files:
            file_status.state = FileState.UPLOADING

        try:
            # Perform upload
            result = self.client.upload_batch(
                file_paths,
                batch.processing_options,
                progress_callback
            )

            # Update batch ID
            batch.batch_id = result.get("batch_id")
            logger.info(f"Batch uploaded with ID: {batch.batch_id}")

            # Update file statuses based on upload results
            uploads = result.get("uploads", [])
            for upload_result in uploads:
                filename = upload_result["file"]
                file_status = batch.get_file_by_name(filename)

                if file_status:
                    if upload_result["status"] == "success":
                        file_status.state = FileState.PROCESSING
                        logger.debug(f"File {filename} uploaded successfully")
                    else:
                        file_status.state = FileState.FAILED
                        file_status.error_message = upload_result.get("error", "Unknown error")
                        logger.warning(f"File {filename} upload failed: {file_status.error_message}")

        except Exception as e:
            logger.error(f"Upload batch failed: {e}", exc_info=True)
            # Mark all files as failed
            for file_status in batch.files:
                if file_status.state == FileState.UPLOADING:
                    file_status.state = FileState.FAILED
                    file_status.error_message = str(e)
            raise
