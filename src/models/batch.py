"""
Data models for batch processing.

This module defines dataclasses for representing batch operations,
file information, and processing results.
"""

from dataclasses import dataclass, field
from typing import Optional, List
from ..config.constants import FileState, FileStatusLocal


@dataclass
class FileInfo:
    """
    Information about a single file in a batch.

    Attributes:
        filename: Name of the file
        file_path: Local path to the file
        state: Current processing state on the server
        status_local: Local UI status
        error_message: Error message if processing failed
        zip_url: Download URL for processed results
    """

    filename: str
    file_path: str
    state: FileState = FileState.PENDING
    status_local: FileStatusLocal = FileStatusLocal.READY
    error_message: Optional[str] = None
    zip_url: Optional[str] = None

    def is_final_state(self) -> bool:
        """
        Check if file is in a final state (no more updates expected).

        Returns:
            True if file is completed, failed, or download failed
        """
        return self.status_local in [
            FileStatusLocal.COMPLETED,
            FileStatusLocal.FAILED,
            FileStatusLocal.DOWNLOAD_FAILED,
        ]

    def update_from_api(self, api_data: dict) -> None:
        """
        Update file info from API response.

        Args:
            api_data: Dictionary from API extract_result response
        """
        state_str = api_data.get("state", "pending")
        try:
            self.state = FileState(state_str)
        except ValueError:
            # Unknown state - keep current
            pass

        if self.state == FileState.DONE:
            self.zip_url = api_data.get("full_zip_url")
        elif self.state == FileState.FAILED:
            self.error_message = api_data.get("err_msg", "Unknown error")


@dataclass
class BatchInfo:
    """
    Information about a batch upload operation.

    Attributes:
        batch_id: Unique identifier for the batch
        files: List of files in the batch
        upload_results: Results from upload operation
    """

    batch_id: Optional[str] = None
    files: List[FileInfo] = field(default_factory=list)
    upload_results: List[dict] = field(default_factory=list)

    def add_file(self, file_path: str) -> FileInfo:
        """
        Add a file to the batch.

        Args:
            file_path: Absolute path to the file

        Returns:
            Created FileInfo instance
        """
        import os
        filename = os.path.basename(file_path)
        file_info = FileInfo(filename=filename, file_path=file_path)
        self.files.append(file_info)
        return file_info

    def get_file_by_name(self, filename: str) -> Optional[FileInfo]:
        """
        Find a file by its filename.

        Args:
            filename: Name of the file to find

        Returns:
            FileInfo if found, None otherwise
        """
        for file_info in self.files:
            if file_info.filename == filename:
                return file_info
        return None

    def get_files_in_progress(self) -> List[FileInfo]:
        """
        Get all files that are still being processed.

        Returns:
            List of files not yet in final state
        """
        return [f for f in self.files if not f.is_final_state()]

    def all_files_complete(self) -> bool:
        """
        Check if all files in the batch are complete.

        Returns:
            True if all files are in final state
        """
        return all(f.is_final_state() for f in self.files)

    def get_success_count(self) -> int:
        """Get count of successfully completed files."""
        return sum(
            1 for f in self.files
            if f.status_local == FileStatusLocal.COMPLETED
        )

    def get_failed_count(self) -> int:
        """Get count of failed files."""
        return sum(
            1 for f in self.files
            if f.status_local in [FileStatusLocal.FAILED, FileStatusLocal.DOWNLOAD_FAILED]
        )
