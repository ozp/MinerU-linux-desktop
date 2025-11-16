"""
MinerU API Client Module

This module provides the MineruClient class for interacting with the MinerU API.
Handles all API operations including authentication, file upload, status checking,
and result downloads.
"""

import configparser
import os
import requests


class MineruClient:
    """
    Client for interacting with the MinerU API.

    This class handles all communication with the MinerU service,
    including file uploads, processing status checks, and result downloads.
    """

    CONFIG_FILE = "config.ini"

    def __init__(self):
        """Initialize the MinerU client."""
        self.api_token = None
        self.is_ocr = False
        self.enable_formula = False
        self.enable_table = False
        self.language = "en"
        self.load_config()

    def load_config(self):
        """Load configuration from config.ini file."""
        if not os.path.exists(self.CONFIG_FILE):
            return

        config = configparser.ConfigParser()
        config.read(self.CONFIG_FILE)

        if "API" in config:
            self.api_token = config["API"].get("token", "")

        if "Processing" in config:
            self.is_ocr = config["Processing"].getboolean("is_ocr", False)
            self.enable_formula = config["Processing"].getboolean("enable_formula", False)
            self.enable_table = config["Processing"].getboolean("enable_table", False)
            self.language = config["Processing"].get("language", "en")

    def get_headers(self):
        """
        Get HTTP headers with authorization token.

        Returns:
            dict: Headers including Authorization bearer token
        """
        if not self.api_token:
            raise ValueError("API token not configured. Please set it in Settings.")

        return {
            "Authorization": f"Bearer {self.api_token}"
        }

    def get_processing_options(self):
        """
        Get current processing options.

        Returns:
            dict: Processing configuration options
        """
        return {
            "is_ocr": self.is_ocr,
            "enable_formula": self.enable_formula,
            "enable_table": self.enable_table,
            "language": self.language
        }
