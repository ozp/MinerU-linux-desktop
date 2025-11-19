"""
Upload worker module.

Background thread for uploading files without blocking the UI.
"""

from PySide6.QtCore import QThread, Signal

from mineru_desktop.services.upload_service import UploadService
from mineru_desktop.models.batch import Batch
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class UploadWorker(QThread):
    """Worker thread for uploading files to MinerU API."""

    # Qt Signals
    progress_updated = Signal(int)  # Progress percentage (0-100)
    upload_completed = Signal(dict)  # Upload result dictionary
    upload_failed = Signal(str)  # Error message

    def __init__(self, upload_service: UploadService, batch: Batch):
        """
        Initialize upload worker.

        Args:
            upload_service: Service for handling uploads
            batch: Batch object containing files to upload
        """
        super().__init__()
        self.upload_service = upload_service
        self.batch = batch
        logger.debug("UploadWorker initialized")

    def run(self) -> None:
        """
        Execute the upload in a separate thread.

        This method runs in a background thread and should not
        interact with the UI directly. Use signals to communicate
        with the main thread.
        """
        logger.info("UploadWorker started")

        try:
            def progress_callback(progress: int) -> None:
                """Forward progress updates to the main thread."""
                self.progress_updated.emit(progress)

            # Perform upload
            self.upload_service.upload_batch(self.batch, progress_callback)

            # Prepare result for main thread
            result = {
                "batch_id": self.batch.batch_id,
                "uploads": [
                    {
                        "file": fs.filename,
                        "status": "success" if fs.state.value in ["processing", "uploaded"]
                                 else "failed",
                        "error": fs.error_message
                    }
                    for fs in self.batch.files
                ]
            }

            logger.info("UploadWorker completed successfully")
            self.upload_completed.emit(result)

        except Exception as e:
            logger.error(f"UploadWorker failed: {e}", exc_info=True)
            self.upload_failed.emit(str(e))
