"""
Configuration management module.

Handles loading and saving application settings from config.ini and keyring.
"""

import configparser
import os
from pathlib import Path
from typing import Optional
import keyring

from mineru_desktop.models.batch import ProcessingOptions, ModelVersion, Language
from mineru_desktop.utils.logging_config import get_logger

logger = get_logger(__name__)


class ConfigManager:
    """
    Manages application configuration.

    Handles both secure storage (keyring) for sensitive data like API tokens
    and file-based storage (config.ini) for non-sensitive settings.
    """

    CONFIG_FILE = "config.ini"
    KEYRING_SERVICE = "MinerU"
    KEYRING_USERNAME = "api_token"

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration manager.

        Args:
            config_file: Optional path to config file (default: config.ini)
        """
        self.config_file = config_file or self.CONFIG_FILE
        self.config = configparser.ConfigParser()
        logger.debug(f"ConfigManager initialized with file: {self.config_file}")

    def load_api_token(self) -> Optional[str]:
        """
        Load API token from secure keyring storage.

        Returns:
            API token if found, None otherwise
        """
        try:
            token = keyring.get_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME)
            if token:
                logger.info("API token loaded from keyring")
            else:
                logger.warning("No API token found in keyring")
            return token
        except Exception as e:
            logger.error(f"Failed to load token from keyring: {e}")
            return None

    def save_api_token(self, token: str) -> None:
        """
        Save API token to secure keyring storage.

        Args:
            token: API token to save

        Raises:
            ValueError: If token is empty
            Exception: If keyring storage fails
        """
        if not token or not token.strip():
            raise ValueError("API token cannot be empty")

        try:
            keyring.set_password(self.KEYRING_SERVICE, self.KEYRING_USERNAME, token)
            logger.info("API token saved to keyring")
        except Exception as e:
            logger.error(f"Failed to save token to keyring: {e}")
            raise

    def load_processing_options(self) -> ProcessingOptions:
        """
        Load processing options from config file.

        Returns:
            ProcessingOptions with loaded or default values
        """
        if not os.path.exists(self.config_file):
            logger.info("Config file not found, using defaults")
            return ProcessingOptions()

        try:
            self.config.read(self.config_file)

            if "Settings" not in self.config:
                logger.info("Settings section not found, using defaults")
                return ProcessingOptions()

            settings = self.config["Settings"]

            # Parse model version
            model_str = settings.get("model_version", "pipeline")
            try:
                model_version = ModelVersion(model_str)
            except ValueError:
                logger.warning(f"Invalid model version '{model_str}', using default")
                model_version = ModelVersion.PIPELINE

            # Parse language
            lang_str = settings.get("language", "pt")
            try:
                language = Language(lang_str)
            except ValueError:
                logger.warning(f"Invalid language '{lang_str}', using default")
                language = Language.PORTUGUESE

            options = ProcessingOptions(
                is_ocr=settings.getboolean("is_ocr", True),
                enable_formula=settings.getboolean("enable_formula", False),
                enable_table=settings.getboolean("enable_table", True),
                language=language,
                model_version=model_version
            )

            logger.info(f"Loaded processing options: OCR={options.is_ocr}, "
                       f"Formula={options.enable_formula}, Table={options.enable_table}, "
                       f"Model={options.model_version.value}")
            return options

        except Exception as e:
            logger.error(f"Error loading processing options: {e}")
            return ProcessingOptions()

    def load_output_directory(self) -> str:
        """
        Load output directory path from config file.

        Returns:
            Expanded path to output directory
        """
        default_dir = "~/Documents/MinerU_Output"

        if not os.path.exists(self.config_file):
            logger.info(f"Config file not found, using default output directory: {default_dir}")
            return os.path.expanduser(default_dir)

        try:
            self.config.read(self.config_file)

            if "Paths" in self.config:
                output_dir = self.config["Paths"].get("output_directory", default_dir)
                expanded_path = os.path.expanduser(output_dir)
                logger.info(f"Loaded output directory: {expanded_path}")
                return expanded_path

        except Exception as e:
            logger.error(f"Error loading output directory: {e}")

        return os.path.expanduser(default_dir)

    def save_settings(
        self,
        processing_options: ProcessingOptions,
        output_directory: str
    ) -> None:
        """
        Save processing options and output directory to config file.

        Args:
            processing_options: Processing options to save
            output_directory: Output directory path

        Raises:
            Exception: If saving fails
        """
        try:
            # Ensure output directory exists
            expanded_path = os.path.expanduser(output_directory)
            Path(expanded_path).mkdir(parents=True, exist_ok=True)

            # Create config structure
            self.config["Settings"] = {
                "is_ocr": str(processing_options.is_ocr),
                "enable_formula": str(processing_options.enable_formula),
                "enable_table": str(processing_options.enable_table),
                "language": processing_options.language.value,
                "model_version": processing_options.model_version.value
            }

            self.config["Paths"] = {
                "output_directory": output_directory
            }

            # Write to file
            with open(self.config_file, "w") as configfile:
                self.config.write(configfile)

            logger.info("Settings saved successfully")

        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            raise

    def get_theme_preference(self) -> str:
        """
        Get theme preference from config.

        Returns:
            Theme name ("light" or "dark")
        """
        if not os.path.exists(self.config_file):
            return "light"

        try:
            self.config.read(self.config_file)
            if "UI" in self.config:
                theme = self.config["UI"].get("theme", "light")
                logger.debug(f"Loaded theme preference: {theme}")
                return theme
        except Exception as e:
            logger.error(f"Error loading theme preference: {e}")

        return "light"

    def save_theme_preference(self, theme: str) -> None:
        """
        Save theme preference to config.

        Args:
            theme: Theme name ("light" or "dark")
        """
        try:
            if not os.path.exists(self.config_file):
                self.config.read(self.config_file)

            if "UI" not in self.config:
                self.config["UI"] = {}

            self.config["UI"]["theme"] = theme

            with open(self.config_file, "w") as configfile:
                self.config.write(configfile)

            logger.info(f"Theme preference saved: {theme}")

        except Exception as e:
            logger.error(f"Failed to save theme preference: {e}")
