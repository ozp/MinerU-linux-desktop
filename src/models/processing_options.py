"""
Data models for processing options and configuration.

This module defines dataclasses for processing configuration
that can be sent to the MinerU API.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from ..config.constants import ModelVersion, Language


@dataclass
class ProcessingOptions:
    """
    Configuration options for document processing.

    Attributes:
        is_ocr: Enable OCR (Optical Character Recognition)
        enable_formula: Enable mathematical formula recognition
        enable_table: Enable table detection and extraction
        model_version: Processing model to use (pipeline or vlm)
        language: OCR language (only for pipeline model)
    """

    is_ocr: bool = True
    enable_formula: bool = False
    enable_table: bool = True
    model_version: ModelVersion = ModelVersion.PIPELINE
    language: Language = Language.PORTUGUESE

    def to_batch_params(self) -> Dict[str, Any]:
        """
        Convert to dictionary for batch-level API parameters.

        Note: is_ocr is NOT included here as it must be set at the file level
        according to the API specification.

        Returns:
            Dictionary with batch-level parameters
        """
        params = {
            "enable_formula": self.enable_formula,
            "enable_table": self.enable_table,
            "model_version": self.model_version.value,
        }

        # Only include language for pipeline model
        if self.model_version == ModelVersion.PIPELINE:
            params["language"] = self.language.value

        return params

    def to_file_params(self) -> Dict[str, Any]:
        """
        Convert to dictionary for file-level API parameters.

        Returns:
            Dictionary with file-level parameters (currently only is_ocr)
        """
        return {
            "is_ocr": self.is_ocr
        }

    @classmethod
    def from_config(cls, config_dict: Dict[str, Any]) -> "ProcessingOptions":
        """
        Create ProcessingOptions from a configuration dictionary.

        Args:
            config_dict: Dictionary with configuration values

        Returns:
            New ProcessingOptions instance
        """
        # Convert string values to enums
        model_str = config_dict.get("model_version", "pipeline")
        try:
            model_version = ModelVersion(model_str)
        except ValueError:
            model_version = ModelVersion.PIPELINE

        language_str = config_dict.get("language", "pt")
        try:
            language = Language(language_str)
        except ValueError:
            language = Language.PORTUGUESE

        return cls(
            is_ocr=config_dict.get("is_ocr", True),
            enable_formula=config_dict.get("enable_formula", False),
            enable_table=config_dict.get("enable_table", True),
            model_version=model_version,
            language=language,
        )

    def validate(self) -> None:
        """
        Validate processing options.

        Raises:
            ValueError: If configuration is invalid
        """
        # VLM model doesn't support language configuration
        if self.model_version == ModelVersion.VLM and self.language != Language.ENGLISH:
            raise ValueError(
                "VLM model does not support language configuration. "
                "Language will be ignored."
            )
