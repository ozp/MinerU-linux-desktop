"""
Data models for batch processing.

This module defines the core data structures used throughout the application.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, List, Dict, Any
from datetime import datetime


class FileState(str, Enum):
    """Enum representing the state of a file in processing."""

    READY = "ready"
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PENDING = "pending"
    DONE = "done"
    COMPLETED = "completed"
    FAILED = "failed"
    DOWNLOAD_FAILED = "download_failed"


class ModelVersion(str, Enum):
    """Enum for MinerU model versions."""

    PIPELINE = "pipeline"
    VLM = "vlm"


class Language(str, Enum):
    """Enum for OCR languages."""

    CHINESE = "ch"
    ENGLISH = "en"
    PORTUGUESE = "pt"


@dataclass
class ProcessingOptions:
    """
    Configuration options for document processing.

    Attributes:
        is_ocr: Enable Optical Character Recognition
        enable_formula: Enable formula recognition
        enable_table: Enable table recognition
        language: OCR language (only for pipeline model)
        model_version: MinerU model version to use
    """

    is_ocr: bool = True
    enable_formula: bool = False
    enable_table: bool = True
    language: Language = Language.PORTUGUESE
    model_version: ModelVersion = ModelVersion.PIPELINE

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert processing options to API-compatible dictionary.

        Returns:
            Dictionary with processing options
        """
        options = {
            "enable_formula": self.enable_formula,
            "enable_table": self.enable_table,
            "model_version": self.model_version.value
        }

        # Only include language for pipeline model
        if self.model_version == ModelVersion.PIPELINE:
            options["language"] = self.language.value

        return options


@dataclass
class FileStatus:
    """
    Status information for a single file.

    Attributes:
        filename: Name of the file
        file_path: Local path to the file
        state: Current processing state
        error_message: Error message if failed
        upload_url: Presigned URL for upload
        download_url: URL for downloading results
        uploaded_at: Timestamp when uploaded
        completed_at: Timestamp when completed
    """

    filename: str
    file_path: str
    state: FileState = FileState.READY
    error_message: Optional[str] = None
    upload_url: Optional[str] = None
    download_url: Optional[str] = None
    uploaded_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def is_final_state(self) -> bool:
        """
        Check if the file is in a final state.

        Returns:
            True if file processing is complete (success or failure)
        """
        return self.state in [
            FileState.COMPLETED,
            FileState.FAILED,
            FileState.DOWNLOAD_FAILED
        ]

    def get_display_status(self) -> str:
        """
        Get human-readable status string.

        Returns:
            Formatted status string for UI display
        """
        status_map = {
            FileState.READY: "Pronto",
            FileState.UPLOADING: "Enviando...",
            FileState.UPLOADED: "Enviado - Processando...",
            FileState.PROCESSING: "Processando no servidor...",
            FileState.PENDING: "Na fila...",
            FileState.DONE: "Baixando...",
            FileState.COMPLETED: "Concluído",
            FileState.FAILED: f"Falha - {self.error_message or 'Erro desconhecido'}",
            FileState.DOWNLOAD_FAILED: f"Erro no Download - {self.error_message or 'Erro desconhecido'}"
        }
        return status_map.get(self.state, str(self.state))


@dataclass
class Batch:
    """
    Represents a batch of files for processing.

    Attributes:
        batch_id: Unique identifier for the batch
        files: List of file statuses
        processing_options: Options for processing
        created_at: Timestamp when batch was created
        completed_at: Timestamp when all files completed
    """

    batch_id: Optional[str] = None
    files: List[FileStatus] = field(default_factory=list)
    processing_options: ProcessingOptions = field(default_factory=ProcessingOptions)
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def add_file(self, file_path: str) -> FileStatus:
        """
        Add a file to the batch.

        Args:
            file_path: Path to the file to add

        Returns:
            Created FileStatus object
        """
        import os
        filename = os.path.basename(file_path)
        file_status = FileStatus(filename=filename, file_path=file_path)
        self.files.append(file_status)
        return file_status

    def get_file_by_name(self, filename: str) -> Optional[FileStatus]:
        """
        Find a file by its filename.

        Args:
            filename: Name of the file to find

        Returns:
            FileStatus if found, None otherwise
        """
        for file_status in self.files:
            if file_status.filename == filename:
                return file_status
        return None

    def all_files_completed(self) -> bool:
        """
        Check if all files have reached a final state.

        Returns:
            True if all files are completed or failed
        """
        if not self.files:
            return False
        return all(f.is_final_state() for f in self.files)

    def get_success_count(self) -> int:
        """
        Get count of successfully completed files.

        Returns:
            Number of files in COMPLETED state
        """
        return sum(1 for f in self.files if f.state == FileState.COMPLETED)

    def get_failed_count(self) -> int:
        """
        Get count of failed files.

        Returns:
            Number of files in FAILED or DOWNLOAD_FAILED state
        """
        return sum(
            1 for f in self.files
            if f.state in [FileState.FAILED, FileState.DOWNLOAD_FAILED]
        )

    def get_processing_count(self) -> int:
        """
        Get count of files still processing.

        Returns:
            Number of files not in final state
        """
        return sum(1 for f in self.files if not f.is_final_state())
