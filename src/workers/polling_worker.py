"""
Polling Worker for Batch Status Monitoring.

This module provides a timer-based worker for periodically checking
the processing status of a batch without blocking the UI.
"""

from typing import Optional
from PySide6.QtCore import QObject, QTimer, Signal

from ..services.batch_service import BatchService
from ..models.batch import BatchInfo
from ..config.constants import POLLING_INTERVAL_MS
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class PollingWorker(QObject):
    """
    Worker for polling batch processing status.

    This worker uses a QTimer to periodically check the status of a batch
    being processed by the MinerU API. It emits signals when the status
    changes or when processing is complete.

    Signals:
        status_updated: Emitted when batch status changes
        all_complete: Emitted when all files in batch are complete
        error_occurred: Emitted when an error occurs during polling
    """

    # Type hints for signals
    status_updated = Signal(object)  # BatchInfo
    all_complete = Signal(object)  # BatchInfo
    error_occurred = Signal(str)

    def __init__(
        self,
        batch: BatchInfo,
        batch_service: Optional[BatchService] = None,
        interval_ms: int = POLLING_INTERVAL_MS
    ) -> None:
        """
        Initialize the polling worker.

        Args:
            batch: BatchInfo instance to monitor
            batch_service: Optional batch service (creates new one if not provided)
            interval_ms: Polling interval in milliseconds (default: 10 seconds)
        """
        super().__init__()
        self.batch = batch
        self.batch_service = batch_service or BatchService()
        self.interval_ms = interval_ms

        # Create timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._check_status)
        self.timer.setInterval(interval_ms)

        logger.debug(f"Polling worker created for batch {batch.batch_id} "
                    f"(interval: {interval_ms}ms)")

    def start(self) -> None:
        """
        Start polling for batch status.

        This starts the timer and immediately checks the status once.
        """
        logger.info(f"Starting polling for batch {self.batch.batch_id}")
        self.timer.start()
        # Check status immediately
        self._check_status()

    def stop(self) -> None:
        """Stop polling."""
        if self.timer.isActive():
            logger.info(f"Stopping polling for batch {self.batch.batch_id}")
            self.timer.stop()

    def is_active(self) -> bool:
        """
        Check if polling is active.

        Returns:
            True if timer is running
        """
        return self.timer.isActive()

    def _check_status(self) -> None:
        """
        Check batch status and emit appropriate signals.

        This method is called by the timer at regular intervals.
        """
        try:
            logger.debug(f"Checking status for batch {self.batch.batch_id}")

            # Check batch status (updates batch in-place)
            all_done = self.batch_service.check_batch_status(self.batch)

            # Emit status update
            self.status_updated.emit(self.batch)

            # Check if all files are complete
            if all_done:
                logger.info(f"Batch {self.batch.batch_id} completed")
                self.stop()
                self.all_complete.emit(self.batch)

        except Exception as e:
            logger.error(f"Error during polling: {e}", exc_info=True)
            self.error_occurred.emit(str(e))
            # Don't stop polling on errors - continue trying

    def cleanup(self) -> None:
        """
        Clean up resources.

        This method should be called when the worker is no longer needed.
        It stops the timer and disconnects signals.
        """
        self.stop()

        # Disconnect signals safely
        try:
            self.timer.timeout.disconnect()
        except:
            pass  # Ignore if no connections exist

        logger.debug(f"Polling worker cleaned up for batch {self.batch.batch_id}")
