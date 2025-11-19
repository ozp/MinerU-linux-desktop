"""
Download service module.

Handles result download operations.
"""

import os
from typing import Optional

from mineru_desktop.core.client import MineruClient
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class DownloadService:
    """Service for handling file downloads."""

    def __init__(self, client: MineruClient, output_directory: str):
        """
        Initialize download service.

        Args:
            client: MinerU API client
            output_directory: Directory for downloaded files
        """
        self.client = client
        self.output_directory = output_directory
        logger.debug(f"DownloadService initialized with output_dir: {output_directory}")

    def download_file(
        self,
        zip_url: str,
        filename: str
    ) -> str:
        """
        Download a result file.

        Args:
            zip_url: URL to download from
            filename: Name for the downloaded file

        Returns:
            Path to downloaded file

        Raises:
            Exception: If download fails
        """
        logger.info(f"Downloading file: {filename}")

        # Ensure output directory exists
        os.makedirs(self.output_directory, exist_ok=True)

        # Create full output path
        output_path = os.path.join(self.output_directory, filename)

        try:
            result_path = self.client.download_result(zip_url, output_path)
            logger.info(f"File downloaded successfully: {result_path}")
            return result_path

        except Exception as e:
            logger.error(f"Download failed for {filename}: {e}", exc_info=True)
            raise

    def set_output_directory(self, directory: str) -> None:
        """
        Update the output directory.

        Args:
            directory: New output directory path
        """
        self.output_directory = directory
        logger.info(f"Output directory updated: {directory}")
