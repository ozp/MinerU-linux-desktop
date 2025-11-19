"""
Upload Worker for Background File Upload.

This module provides a QThread worker for uploading files
to the MinerU API without blocking the UI.
"""

from typing import Optional
from PySide6.QtCore import QThread, Signal

from ..services.batch_service import BatchService
from ..models.batch import BatchInfo
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class UploadWorker(QThread):
    """
    Worker thread for uploading files to MinerU API.

    This worker runs in a separate thread to prevent blocking the UI
    during file uploads. It emits signals to communicate progress and
    completion status back to the main thread.

    Signals:
        progress_updated: Emitted with progress percentage (0-100)
        upload_completed: Emitted with BatchInfo when upload succeeds
        upload_failed: Emitted with error message when upload fails
    """

    # Type hints for signals
    progress_updated = Signal(int)
    upload_completed = Signal(object)  # BatchInfo
    upload_failed = Signal(str)

    def __init__(
        self,
        batch: BatchInfo,
        batch_service: Optional[BatchService] = None
    ) -> None:
        """
        Initialize the upload worker.

        Args:
            batch: BatchInfo instance with files to upload
            batch_service: Optional batch service (creates new one if not provided)
        """
        super().__init__()
        self.batch = batch
        self.batch_service = batch_service or BatchService()
        logger.debug(f"Upload worker created for batch with {len(batch.files)} files")

    def run(self) -> None:
        """
        Execute the upload in a separate thread.

        This method runs in the worker thread and performs the upload
        operation. It emits signals to update the UI with progress and results.
        """
        try:
            logger.info("Upload worker started")

            # Upload batch with progress callback
            def progress_callback(progress: int) -> None:
                """Callback to emit progress updates."""
                self.progress_updated.emit(progress)

            self.batch_service.upload_batch(self.batch, progress_callback)

            # Emit completion signal
            logger.info("Upload worker completed successfully")
            self.upload_completed.emit(self.batch)

        except Exception as e:
            logger.error(f"Upload worker failed: {e}", exc_info=True)
            self.upload_failed.emit(str(e))
