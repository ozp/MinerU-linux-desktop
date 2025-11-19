"""
Constants and Enumerations for MinerU Desktop Client.

This module centralizes all constants, enums, and configuration values
used throughout the application to avoid magic strings and ensure type safety.
"""

from enum import Enum


class FileState(str, Enum):
    """Processing state of a file on the API server."""

    PENDING = "pending"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class FileStatusLocal(str, Enum):
    """Local status of a file in the UI."""

    READY = "ready"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DOWNLOAD_FAILED = "download_failed"


class ModelVersion(str, Enum):
    """Available MinerU processing models."""

    PIPELINE = "pipeline"  # Legacy model with language support
    VLM = "vlm"  # New model without language configuration


class Language(str, Enum):
    """Supported OCR languages (Pipeline model only)."""

    CHINESE = "ch"
    ENGLISH = "en"
    PORTUGUESE = "pt"


# Application Configuration
APP_NAME = "MinerU Desktop Client"
APP_AUTHOR = "MinerU"

# API Configuration
API_BASE_URL = "https://mineru.net/api/v4"
API_TIMEOUT_DEFAULT = 30
API_TIMEOUT_UPLOAD = 300
API_TIMEOUT_DOWNLOAD = 300

# Keyring Configuration
KEYRING_SERVICE = "MinerU"
KEYRING_USERNAME = "api_token"

# File Configuration
CONFIG_FILE = "config.ini"
DEFAULT_OUTPUT_DIR = "~/Documents/MinerU_Output"

# Processing Configuration
POLLING_INTERVAL_MS = 10000  # 10 seconds
MAX_UPLOAD_WORKERS = 5
DOWNLOAD_CHUNK_SIZE = 8192

# UI Text (Portuguese)
UI_TEXT = {
    "add_files": "Adicionar Arquivos...",
    "remove_selected": "Remover Selecionados",
    "start_processing": "Iniciar Processamento",
    "open_output": "Abrir Pasta de Saída",
    "settings": "Configurações",
    "about": "Sobre",
    "exit": "Sair",
    "file_selection": "File Selection",
    "processing": "Processing",
}

# Status Display Text (Portuguese)
STATUS_TEXT = {
    FileStatusLocal.READY: "Pronto",
    FileStatusLocal.UPLOADING: "Enviando",
    FileStatusLocal.PROCESSING: "Processando no servidor...",
    FileStatusLocal.COMPLETED: "Concluído",
    FileStatusLocal.FAILED: "Falhou",
    FileStatusLocal.DOWNLOAD_FAILED: "Erro no Download",
}

# File Type Filters
FILE_FILTERS = (
    "Documentos (*.pdf *.docx *.pptx);;"
    "Imagens (*.jpg *.png);;"
    "Todos os Arquivos (*)"
)
