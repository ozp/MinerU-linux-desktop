"""
Configuration Manager for MinerU Desktop Client.

This module provides a centralized configuration system that handles:
- Loading/saving configuration from config.ini
- Secure token storage using keyring
- Processing options management
- Output directory configuration

This eliminates the duplication of CONFIG_FILE, KEYRING_* constants
across multiple modules.
"""

import configparser
import os
from pathlib import Path
from typing import Optional
import keyring

from .constants import (
    CONFIG_FILE,
    KEYRING_SERVICE,
    KEYRING_USERNAME,
    DEFAULT_OUTPUT_DIR,
    ModelVersion,
    Language,
)
from ..models.processing_options import ProcessingOptions
from ..utils.logging_config import get_logger


logger = get_logger(__name__)


class ConfigManager:
    """
    Centralized configuration manager.

    This class is a singleton that manages all application configuration,
    including secure token storage via keyring and non-sensitive settings
    in config.ini.
    """

    _instance: Optional["ConfigManager"] = None

    def __new__(cls) -> "ConfigManager":
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the configuration manager."""
        if self._initialized:
            return

        self._initialized = True
        self._api_token: Optional[str] = None
        self._output_directory: str = os.path.expanduser(DEFAULT_OUTPUT_DIR)
        self._processing_options = ProcessingOptions()

        # Load configuration on initialization
        self.load()

    @property
    def api_token(self) -> Optional[str]:
        """Get the API token from secure storage."""
        return self._api_token

    @api_token.setter
    def api_token(self, value: Optional[str]) -> None:
        """Set the API token and save to secure storage."""
        self._api_token = value
        if value:
            try:
                keyring.set_password(KEYRING_SERVICE, KEYRING_USERNAME, value)
                logger.info("API token saved to keyring")
            except Exception as e:
                logger.error(f"Failed to save token to keyring: {e}")
                raise

    @property
    def output_directory(self) -> str:
        """Get the output directory path."""
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value: str) -> None:
        """Set the output directory."""
        self._output_directory = os.path.expanduser(value)

    @property
    def processing_options(self) -> ProcessingOptions:
        """Get current processing options."""
        return self._processing_options

    @processing_options.setter
    def processing_options(self, value: ProcessingOptions) -> None:
        """Set processing options."""
        self._processing_options = value

    def load(self) -> None:
        """
        Load configuration from keyring and config file.

        This method loads:
        - API token from system keyring (secure)
        - Processing options from config.ini
        - Output directory from config.ini
        """
        # Load token from keyring
        try:
            token = keyring.get_password(KEYRING_SERVICE, KEYRING_USERNAME)
            if token:
                self._api_token = token
                logger.info("API token loaded from keyring")
            else:
                logger.warning("No API token found in keyring")
        except Exception as e:
            logger.warning(f"Could not load token from keyring: {e}")

        # Load non-sensitive settings from config.ini
        if not os.path.exists(CONFIG_FILE):
            logger.info(f"Config file {CONFIG_FILE} not found, using defaults")
            return

        try:
            config = configparser.ConfigParser()
            config.read(CONFIG_FILE)

            # Load processing options
            if "Settings" in config:
                settings = config["Settings"]
                config_dict = {
                    "is_ocr": settings.getboolean("is_ocr", True),
                    "enable_formula": settings.getboolean("enable_formula", False),
                    "enable_table": settings.getboolean("enable_table", True),
                    "model_version": settings.get("model_version", "pipeline"),
                    "language": settings.get("language", "pt"),
                }
                self._processing_options = ProcessingOptions.from_config(config_dict)
                logger.info("Processing options loaded from config")

            # Load output directory
            if "Paths" in config:
                output_dir = config["Paths"].get("output_directory", DEFAULT_OUTPUT_DIR)
                self._output_directory = os.path.expanduser(output_dir)
                logger.info(f"Output directory set to: {self._output_directory}")

        except Exception as e:
            logger.error(f"Error loading config file: {e}", exc_info=True)

    def save(self) -> None:
        """
        Save configuration to config file.

        Note: API token is saved separately via the api_token setter.
        This method only saves non-sensitive settings to config.ini.
        """
        try:
            config = configparser.ConfigParser()

            # Save processing options
            config["Settings"] = {
                "is_ocr": str(self._processing_options.is_ocr),
                "enable_formula": str(self._processing_options.enable_formula),
                "enable_table": str(self._processing_options.enable_table),
                "model_version": self._processing_options.model_version.value,
                "language": self._processing_options.language.value,
            }

            # Save paths
            config["Paths"] = {
                "output_directory": self._output_directory
            }

            # Write to file
            with open(CONFIG_FILE, "w") as configfile:
                config.write(configfile)

            logger.info(f"Configuration saved to {CONFIG_FILE}")

        except Exception as e:
            logger.error(f"Error saving config file: {e}", exc_info=True)
            raise

    def validate(self) -> None:
        """
        Validate current configuration.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self._api_token:
            raise ValueError("API token is not configured")

        if not self._output_directory:
            raise ValueError("Output directory is not configured")

        # Validate processing options
        self._processing_options.validate()

        logger.info("Configuration validated successfully")

    def ensure_output_directory_exists(self) -> None:
        """
        Create output directory if it doesn't exist.

        Raises:
            OSError: If directory cannot be created
        """
        try:
            Path(self._output_directory).mkdir(parents=True, exist_ok=True)
            logger.info(f"Output directory ensured: {self._output_directory}")
        except Exception as e:
            logger.error(f"Failed to create output directory: {e}")
            raise


# Singleton instance getter
def get_config() -> ConfigManager:
    """
    Get the singleton ConfigManager instance.

    Returns:
        ConfigManager instance

    Example:
        >>> config = get_config()
        >>> config.api_token = "my-token"
        >>> config.save()
    """
    return ConfigManager()
