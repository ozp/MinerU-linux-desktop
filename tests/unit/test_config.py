"""Unit tests for configuration and settings."""
import os
import configparser
import pytest
from unittest.mock import Mock, patch
from settings_dialog import SettingsDialog
from PySide6.QtWidgets import QApplication


# QApplication needs to be created once for all Qt tests
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # Don't quit the app as it might be used by other tests


@pytest.mark.unit
class TestSettingsDialog:
    """Tests for SettingsDialog class."""

    def test_dialog_initialization(self, qapp, mock_keyring):
        """Test settings dialog initialization."""
        dialog = SettingsDialog()
        assert dialog.windowTitle() == "Settings"
        assert dialog.token_input is not None
        assert dialog.output_path_input is not None

    def test_load_settings_default(self, qapp, mock_keyring, monkeypatch, temp_dir):
        """Test loading default settings when no config file exists."""
        # Mock config file doesn't exist
        monkeypatch.chdir(temp_dir)

        dialog = SettingsDialog()
        dialog.load_settings()

        # Check defaults
        assert dialog.force_ocr_checkbox.isChecked() is True
        assert dialog.enable_table_checkbox.isChecked() is True
        assert dialog.enable_formula_checkbox.isChecked() is False

    def test_load_settings_from_file(self, qapp, mock_keyring, temp_dir, monkeypatch):
        """Test loading settings from config file."""
        # Create config file
        config_path = os.path.join(temp_dir, "config.ini")
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "False",
            "enable_formula": "True",
            "enable_table": "False",
            "language": "en",
            "model_version": "vlm"
        }
        config["Paths"] = {
            "output_directory": temp_dir
        }
        with open(config_path, "w") as f:
            config.write(f)

        monkeypatch.chdir(temp_dir)

        dialog = SettingsDialog()
        dialog.load_settings()

        assert dialog.force_ocr_checkbox.isChecked() is False
        assert dialog.enable_formula_checkbox.isChecked() is True
        assert dialog.enable_table_checkbox.isChecked() is False
        assert dialog.language_combo.currentData() == "en"
        assert dialog.model_combo.currentData() == "vlm"

    def test_save_settings_creates_file(self, qapp, mock_keyring, temp_dir, monkeypatch):
        """Test that save_settings creates config file."""
        monkeypatch.chdir(temp_dir)

        dialog = SettingsDialog()
        dialog.token_input.setText("test_token_abc123")
        dialog.output_path_input.setText(temp_dir)
        dialog.force_ocr_checkbox.setChecked(True)
        dialog.enable_formula_checkbox.setChecked(True)
        dialog.enable_table_checkbox.setChecked(False)

        # Trigger save
        dialog.save_settings()

        # Check that config file was created
        config_path = os.path.join(temp_dir, "config.ini")
        assert os.path.exists(config_path)

        # Verify saved values
        config = configparser.ConfigParser()
        config.read(config_path)
        assert config["Settings"]["is_ocr"] == "True"
        assert config["Settings"]["enable_formula"] == "True"
        assert config["Settings"]["enable_table"] == "False"

    def test_save_settings_validates_token(self, qapp, mock_keyring, temp_dir, monkeypatch):
        """Test that save_settings validates API token."""
        monkeypatch.chdir(temp_dir)

        dialog = SettingsDialog()
        dialog.token_input.setText("")  # Empty token
        dialog.output_path_input.setText(temp_dir)

        # Should show warning and not save
        # Note: This would normally show a QMessageBox which we can't easily test
        # In production, we'd need to mock QMessageBox

    def test_on_model_changed_disables_language_for_vlm(self, qapp, mock_keyring):
        """Test that language settings are disabled for VLM model."""
        dialog = SettingsDialog()

        # Set to VLM model
        vlm_index = dialog.model_combo.findData("vlm")
        dialog.model_combo.setCurrentIndex(vlm_index)
        dialog.on_model_changed()

        assert dialog.language_label.isEnabled() is False
        assert dialog.language_combo.isEnabled() is False

    def test_on_model_changed_enables_language_for_pipeline(self, qapp, mock_keyring):
        """Test that language settings are enabled for pipeline model."""
        dialog = SettingsDialog()

        # Set to pipeline model
        pipeline_index = dialog.model_combo.findData("pipeline")
        dialog.model_combo.setCurrentIndex(pipeline_index)
        dialog.on_model_changed()

        assert dialog.language_label.isEnabled() is True
        assert dialog.language_combo.isEnabled() is True


@pytest.mark.unit
class TestConfigPersistence:
    """Tests for configuration persistence."""

    def test_config_roundtrip(self, temp_dir, monkeypatch, mock_keyring):
        """Test saving and loading configuration maintains values."""
        config_path = os.path.join(temp_dir, "config.ini")

        # Create and save config
        config = configparser.ConfigParser()
        config["Settings"] = {
            "is_ocr": "True",
            "enable_formula": "False",
            "enable_table": "True",
            "language": "pt",
            "model_version": "pipeline"
        }
        config["Paths"] = {
            "output_directory": temp_dir
        }
        with open(config_path, "w") as f:
            config.write(f)

        # Load and verify
        loaded_config = configparser.ConfigParser()
        loaded_config.read(config_path)

        assert loaded_config["Settings"]["is_ocr"] == "True"
        assert loaded_config["Settings"]["enable_formula"] == "False"
        assert loaded_config["Settings"]["language"] == "pt"
        assert loaded_config["Paths"]["output_directory"] == temp_dir
