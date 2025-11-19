"""
Unit tests for ConfigManager class.

Tests configuration loading, saving, and validation including
keyring integration for API tokens.
"""

import os
import pytest
from unittest.mock import patch, Mock, MagicMock
import configparser

from mineru_desktop.core.config import ConfigManager
from mineru_desktop.models.batch import ProcessingOptions, ModelVersion, Language


@pytest.mark.unit
class TestConfigManager:
    """Test suite for ConfigManager."""

    def test_init_default_config_file(self):
        """Test initialization with default config file."""
        config_manager = ConfigManager()
        assert config_manager.config_file == "config.ini"

    def test_init_custom_config_file(self, temp_config_file):
        """Test initialization with custom config file."""
        config_manager = ConfigManager(config_file=temp_config_file)
        assert config_manager.config_file == temp_config_file

    @patch('mineru_desktop.core.config.keyring.get_password')
    def test_load_api_token_success(self, mock_get_password, config_manager, sample_api_token):
        """Test successful API token loading from keyring."""
        mock_get_password.return_value = sample_api_token

        token = config_manager.load_api_token()

        assert token == sample_api_token
        mock_get_password.assert_called_once_with("MinerU", "api_token")

    @patch('mineru_desktop.core.config.keyring.get_password')
    def test_load_api_token_not_found(self, mock_get_password, config_manager):
        """Test loading API token when not found in keyring."""
        mock_get_password.return_value = None

        token = config_manager.load_api_token()

        assert token is None
        mock_get_password.assert_called_once()

    @patch('mineru_desktop.core.config.keyring.get_password')
    def test_load_api_token_keyring_error(self, mock_get_password, config_manager):
        """Test loading API token with keyring error."""
        mock_get_password.side_effect = Exception("Keyring error")

        token = config_manager.load_api_token()

        assert token is None

    @patch('mineru_desktop.core.config.keyring.set_password')
    def test_save_api_token_success(
        self,
        mock_set_password,
        config_manager,
        sample_api_token
    ):
        """Test successful API token saving to keyring."""
        config_manager.save_api_token(sample_api_token)

        mock_set_password.assert_called_once_with("MinerU", "api_token", sample_api_token)

    @patch('mineru_desktop.core.config.keyring.set_password')
    def test_save_api_token_empty(self, mock_set_password, config_manager):
        """Test saving empty API token raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            config_manager.save_api_token("")

        mock_set_password.assert_not_called()

    @patch('mineru_desktop.core.config.keyring.set_password')
    def test_save_api_token_whitespace(self, mock_set_password, config_manager):
        """Test saving whitespace-only API token raises ValueError."""
        with pytest.raises(ValueError, match="cannot be empty"):
            config_manager.save_api_token("   ")

        mock_set_password.assert_not_called()

    @patch('mineru_desktop.core.config.keyring.set_password')
    def test_save_api_token_keyring_error(
        self,
        mock_set_password,
        config_manager,
        sample_api_token
    ):
        """Test saving API token with keyring error."""
        mock_set_password.side_effect = Exception("Keyring error")

        with pytest.raises(Exception, match="Keyring error"):
            config_manager.save_api_token(sample_api_token)

    def test_load_processing_options_no_file(self, config_manager):
        """Test loading processing options when config file doesn't exist."""
        options = config_manager.load_processing_options()

        assert isinstance(options, ProcessingOptions)
        assert options.is_ocr == True
        assert options.enable_formula == False
        assert options.enable_table == True
        assert options.language == Language.PORTUGUESE
        assert options.model_version == ModelVersion.PIPELINE

    def test_load_processing_options_success(self, temp_config_file):
        """Test successful loading of processing options from file."""
        # Create config file
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "False",
            "enable_formula": "True",
            "enable_table": "False",
            "language": "en",
            "model_version": "vlm"
        }
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        options = config_manager.load_processing_options()

        assert options.is_ocr == False
        assert options.enable_formula == True
        assert options.enable_table == False
        assert options.language == Language.ENGLISH
        assert options.model_version == ModelVersion.VLM

    def test_load_processing_options_no_settings_section(self, temp_config_file):
        """Test loading processing options when Settings section is missing."""
        # Create empty config file
        config = configparser.ConfigParser()
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        options = config_manager.load_processing_options()

        # Should return defaults
        assert isinstance(options, ProcessingOptions)
        assert options.is_ocr == True

    def test_load_processing_options_invalid_model(self, temp_config_file):
        """Test loading processing options with invalid model version."""
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "True",
            "enable_formula": "False",
            "enable_table": "True",
            "language": "pt",
            "model_version": "invalid_model"
        }
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        options = config_manager.load_processing_options()

        # Should use default model
        assert options.model_version == ModelVersion.PIPELINE

    def test_load_processing_options_invalid_language(self, temp_config_file):
        """Test loading processing options with invalid language."""
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "True",
            "enable_formula": "False",
            "enable_table": "True",
            "language": "invalid_lang",
            "model_version": "pipeline"
        }
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        options = config_manager.load_processing_options()

        # Should use default language
        assert options.language == Language.PORTUGUESE

    def test_load_output_directory_no_file(self, config_manager):
        """Test loading output directory when config file doesn't exist."""
        output_dir = config_manager.load_output_directory()

        assert output_dir == os.path.expanduser("~/Documents/MinerU_Output")

    def test_load_output_directory_success(self, temp_config_file, temp_dir):
        """Test successful loading of output directory from file."""
        config = configparser.ConfigParser()
        config["Paths"] = {
            "output_directory": temp_dir
        }
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        output_dir = config_manager.load_output_directory()

        assert output_dir == temp_dir

    def test_load_output_directory_with_tilde(self, temp_config_file):
        """Test loading output directory with tilde expansion."""
        config = configparser.ConfigParser()
        config["Paths"] = {
            "output_directory": "~/test_output"
        }
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        output_dir = config_manager.load_output_directory()

        assert output_dir == os.path.expanduser("~/test_output")
        assert "~" not in output_dir

    def test_save_settings_success(
        self,
        temp_config_file,
        temp_dir,
        sample_processing_options
    ):
        """Test successful saving of settings to file."""
        config_manager = ConfigManager(config_file=temp_config_file)
        output_dir = temp_dir

        config_manager.save_settings(sample_processing_options, output_dir)

        # Verify file was created
        assert os.path.exists(temp_config_file)

        # Verify contents
        config = configparser.ConfigParser()
        config.read(temp_config_file)

        assert config["Settings"]["is_ocr"] == "True"
        assert config["Settings"]["enable_formula"] == "False"
        assert config["Settings"]["enable_table"] == "True"
        assert config["Settings"]["language"] == "pt"
        assert config["Settings"]["model_version"] == "pipeline"
        assert config["Paths"]["output_directory"] == output_dir

    def test_save_settings_creates_directory(
        self,
        temp_config_file,
        temp_dir,
        sample_processing_options
    ):
        """Test that save_settings creates output directory if missing."""
        config_manager = ConfigManager(config_file=temp_config_file)
        new_dir = os.path.join(temp_dir, "new_output")

        config_manager.save_settings(sample_processing_options, new_dir)

        # Verify directory was created
        assert os.path.exists(os.path.expanduser(new_dir))

    def test_get_theme_preference_no_file(self, config_manager):
        """Test getting theme preference when config file doesn't exist."""
        theme = config_manager.get_theme_preference()
        assert theme == "light"

    def test_get_theme_preference_success(self, temp_config_file):
        """Test successful loading of theme preference."""
        config = configparser.ConfigParser()
        config["UI"] = {"theme": "dark"}
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        theme = config_manager.get_theme_preference()

        assert theme == "dark"

    def test_get_theme_preference_no_ui_section(self, temp_config_file):
        """Test getting theme preference when UI section is missing."""
        config = configparser.ConfigParser()
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        theme = config_manager.get_theme_preference()

        assert theme == "light"

    def test_save_theme_preference_success(self, temp_config_file):
        """Test successful saving of theme preference."""
        config_manager = ConfigManager(config_file=temp_config_file)

        config_manager.save_theme_preference("dark")

        # Verify file contents
        config = configparser.ConfigParser()
        config.read(temp_config_file)

        assert config["UI"]["theme"] == "dark"

    def test_save_theme_preference_creates_file(self, temp_config_file):
        """Test that save_theme_preference creates file if missing."""
        config_manager = ConfigManager(config_file=temp_config_file)

        config_manager.save_theme_preference("dark")

        assert os.path.exists(temp_config_file)

    def test_constants(self):
        """Test ConfigManager constants."""
        assert ConfigManager.CONFIG_FILE == "config.ini"
        assert ConfigManager.KEYRING_SERVICE == "MinerU"
        assert ConfigManager.KEYRING_USERNAME == "api_token"

    def test_load_processing_options_partial_config(self, temp_config_file):
        """Test loading processing options with partial configuration."""
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "False",
            # Missing other settings
        }
        with open(temp_config_file, "w") as f:
            config.write(f)

        config_manager = ConfigManager(config_file=temp_config_file)
        options = config_manager.load_processing_options()

        # Should have loaded is_ocr and used defaults for others
        assert options.is_ocr == False
        assert options.enable_formula == False  # default
        assert options.enable_table == True  # default
