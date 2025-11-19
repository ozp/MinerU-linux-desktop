# Padrões de Código - MinerU Desktop Client

Este documento define os padrões de código, convenções e melhores práticas utilizadas no projeto MinerU Desktop Client.

## Índice

- [Estilo de Código Python](#estilo-de-código-python)
- [Padrões de Design](#padrões-de-design)
- [Padrões Qt/PySide6](#padrões-qtpyside6)
- [Tratamento de Erros](#tratamento-de-erros)
- [Logging](#logging)
- [Configuração](#configuração)
- [Threading](#threading)
- [Testes](#testes)
- [Documentação](#documentação)

---

## Estilo de Código Python

### PEP 8 com Adaptações

Seguimos [PEP 8](https://pep8.org/) com as seguintes adaptações:

- **Comprimento de linha**: 100 caracteres (não 79)
- **Aspas**: Preferir aspas duplas `"` para strings
- **Imports**: Agrupados e ordenados alfabeticamente

### Formatação com Black

```python
# Configuração em pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38', 'py39', 'py310', 'py311']
```

**Exemplo**:
```python
# ✅ Bom (formatado com Black)
def long_function_name(
    parameter_one: str,
    parameter_two: int,
    parameter_three: Optional[Dict[str, str]] = None,
) -> List[str]:
    """Função com múltiplos parâmetros."""
    return []


# ❌ Ruim (não formatado)
def long_function_name(parameter_one: str, parameter_two: int, parameter_three: Optional[Dict[str, str]] = None) -> List[str]:
    return []
```

### Type Hints

Usar type hints em todas as assinaturas de função:

```python
from typing import List, Dict, Optional, Callable, Union

# ✅ Bom
def process_files(
    file_paths: List[str],
    callback: Optional[Callable[[int], None]] = None
) -> Dict[str, str]:
    """Process files with optional progress callback."""
    result: Dict[str, str] = {}
    return result


# ❌ Ruim (sem type hints)
def process_files(file_paths, callback=None):
    result = {}
    return result
```

### Docstrings Google Style

```python
def upload_batch(
    self,
    file_paths: List[str],
    progress_callback: Optional[Callable[[int], None]] = None
) -> Dict:
    """Upload a batch of files to MinerU API.

    This method implements a two-step upload process:
    1. POST request to get batch_id and presigned URLs
    2. Parallel PUT requests to upload files

    Args:
        file_paths: List of local file paths to upload
        progress_callback: Optional callback for progress updates (0-100)

    Returns:
        dict: Response containing:
            - batch_id (str): Unique batch identifier
            - uploads (List[dict]): Upload status for each file

    Raises:
        ValueError: If no files provided or token not configured
        ConnectionError: If API connection fails
        TimeoutError: If request times out

    Example:
        >>> client = MineruClient()
        >>> result = client.upload_batch(['doc1.pdf', 'doc2.pdf'])
        >>> print(result['batch_id'])
        'batch_abc123'
    """
    pass
```

### Imports

```python
# ✅ Bom (agrupado e ordenado)
"""Module docstring."""

# Standard library
import os
import sys
from typing import List, Optional

# Third-party
import requests
from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QMainWindow, QWidget

# Local
from mineru_client import MineruClient
from version import VERSION


# ❌ Ruim (não organizado)
from mineru_client import MineruClient
import sys
from PySide6.QtWidgets import QWidget
import os
from typing import List
```

### Naming Conventions

```python
# Classes: PascalCase
class MineruClient:
    pass

class UploadWorker:
    pass


# Functions e Methods: snake_case
def upload_batch():
    pass

def check_batch_status():
    pass


# Constants: UPPER_SNAKE_CASE
API_BASE_URL = "https://mineru.net/api/v4"
MAX_WORKERS = 5
DEFAULT_TIMEOUT = 30


# Private attributes/methods: _leading_underscore
class MyClass:
    def __init__(self):
        self._private_data = None

    def _private_helper(self):
        pass


# Variables: snake_case
file_paths = []
batch_id = None
current_status = "processing"
```

---

## Padrões de Design

### 1. Dependency Injection

Injetar dependências em vez de criar internamente:

```python
# ✅ Bom
class MainWindow(QMainWindow):
    def __init__(self, api_client: Optional[MineruClient] = None):
        super().__init__()
        self.mineru_client = api_client or MineruClient()


# ❌ Ruim
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mineru_client = MineruClient()  # Hard-coded dependency
```

### 2. Composition over Inheritance

Preferir composição a herança:

```python
# ✅ Bom
class FileProcessor:
    def __init__(self, uploader: Uploader, downloader: Downloader):
        self.uploader = uploader
        self.downloader = downloader

    def process(self, files):
        self.uploader.upload(files)
        self.downloader.download()


# ❌ Ruim
class FileProcessor(Uploader, Downloader):
    def process(self, files):
        self.upload(files)
        self.download()
```

### 3. Single Responsibility Principle

Cada classe/função deve ter uma única responsabilidade:

```python
# ✅ Bom
class FileUploader:
    """Handles file upload operations only."""

    def upload_file(self, path: str) -> bool:
        pass


class FileValidator:
    """Validates files only."""

    def is_valid(self, path: str) -> bool:
        pass


# ❌ Ruim
class FileHandler:
    """Does everything."""

    def upload_file(self, path: str) -> bool:
        pass

    def validate_file(self, path: str) -> bool:
        pass

    def download_file(self, url: str) -> str:
        pass

    def extract_file(self, path: str) -> None:
        pass
```

### 4. Open/Closed Principle

Aberto para extensão, fechado para modificação:

```python
# ✅ Bom
class APIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def _make_request(self, endpoint: str, method: str, **kwargs):
        """Base method for requests."""
        pass

class MineruClient(APIClient):
    """Extends APIClient for MinerU-specific operations."""

    def upload_batch(self, files):
        return self._make_request('/batch', 'POST', files=files)


# ❌ Ruim
class MineruClient:
    """Hardcoded for MinerU, difficult to extend."""

    def make_request(self, endpoint: str):
        # Hardcoded logic
        url = f"https://mineru.net{endpoint}"
        # ...
```

### 5. Interface Segregation

Preferir interfaces pequenas e específicas:

```python
# ✅ Bom
class Uploadable(Protocol):
    def upload(self, files: List[str]) -> Dict:
        ...


class Downloadable(Protocol):
    def download(self, url: str) -> str:
        ...


# ❌ Ruim
class FileOperations(Protocol):
    def upload(self, files: List[str]) -> Dict:
        ...

    def download(self, url: str) -> str:
        ...

    def delete(self, path: str) -> None:
        ...

    def move(self, src: str, dst: str) -> None:
        ...
```

---

## Padrões Qt/PySide6

### 1. Signals e Slots

```python
# ✅ Bom
class UploadWorker(QThread):
    progress_updated = Signal(int)
    upload_completed = Signal(dict)
    upload_failed = Signal(str)

    def run(self):
        try:
            result = self.do_upload()
            self.upload_completed.emit(result)
        except Exception as e:
            self.upload_failed.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.worker = UploadWorker()
        self.worker.progress_updated.connect(self.on_progress)
        self.worker.upload_completed.connect(self.on_complete)

    def on_progress(self, value: int):
        self.progress_bar.setValue(value)


# ❌ Ruim (coupling direto)
class UploadWorker(QThread):
    def __init__(self, main_window):
        self.main_window = main_window

    def run(self):
        # ...
        self.main_window.progress_bar.setValue(50)  # Direct coupling
```

### 2. Resource Management

```python
# ✅ Bom
def closeEvent(self, event: QCloseEvent):
    """Clean up resources on close."""
    # Stop timers
    if self.polling_timer:
        if self.polling_timer.isActive():
            self.polling_timer.stop()
        self.polling_timer.deleteLater()
        self.polling_timer = None

    # Wait for workers
    if self.upload_worker and self.upload_worker.isRunning():
        self.upload_worker.wait()

    event.accept()


# ❌ Ruim
def closeEvent(self, event: QCloseEvent):
    event.accept()  # No cleanup
```

### 3. UI Initialization

```python
# ✅ Bom
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._init_attributes()
        self._setup_ui()
        self._connect_signals()

    def _init_attributes(self):
        """Initialize all attributes."""
        self.selected_files = []
        self.current_batch_id = None

    def _setup_ui(self):
        """Setup UI components."""
        self.setWindowTitle("App")
        self._create_menu_bar()
        self._create_central_widget()

    def _connect_signals(self):
        """Connect all signals."""
        self.button.clicked.connect(self.on_click)


# ❌ Ruim
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Everything mixed together
        self.selected_files = []
        self.setWindowTitle("App")
        self.button = QPushButton()
        self.button.clicked.connect(self.on_click)
```

### 4. Thread Safety

```python
# ✅ Bom
class UploadWorker(QThread):
    progress_updated = Signal(int)

    def run(self):
        for i in range(100):
            # Communicate via signals
            self.progress_updated.emit(i)


class MainWindow(QMainWindow):
    def on_progress(self, value: int):
        # UI updates in main thread
        self.progress_bar.setValue(value)


# ❌ Ruim
class UploadWorker(QThread):
    def __init__(self, progress_bar):
        self.progress_bar = progress_bar

    def run(self):
        for i in range(100):
            # Direct UI manipulation from worker thread!
            self.progress_bar.setValue(i)
```

---

## Tratamento de Erros

### 1. Exceções Específicas

```python
# ✅ Bom
class APIError(Exception):
    """Base exception for API errors."""
    pass


class AuthenticationError(APIError):
    """Authentication failed."""
    pass


class NetworkError(APIError):
    """Network connection error."""
    pass


def upload_file(path: str):
    try:
        response = requests.post(url, files={'file': open(path, 'rb')})
        response.raise_for_status()
    except requests.HTTPError as e:
        if e.response.status_code == 401:
            raise AuthenticationError("Invalid token") from e
        raise APIError(f"Upload failed: {e}") from e
    except requests.ConnectionError as e:
        raise NetworkError("Connection failed") from e


# ❌ Ruim
def upload_file(path: str):
    try:
        response = requests.post(url, files={'file': open(path, 'rb')})
    except Exception as e:
        print(f"Error: {e}")  # Generic exception, lost context
        return None
```

### 2. Error Context

```python
# ✅ Bom
def download_result(self, zip_url: str, filename: str) -> str:
    """Download result file.

    Args:
        zip_url: URL to download from
        filename: Target filename

    Returns:
        Path to downloaded file

    Raises:
        ConnectionError: If download fails due to network
        TimeoutError: If download times out
        IOError: If file cannot be written
    """
    try:
        response = requests.get(zip_url, timeout=300, stream=True)
        response.raise_for_status()

        output_path = os.path.join(self.output_directory, filename)
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        return output_path

    except requests.ConnectionError as e:
        raise ConnectionError(
            f"Failed to download from {zip_url}: {e}"
        ) from e
    except requests.Timeout as e:
        raise TimeoutError(
            f"Download timeout for {filename}: {e}"
        ) from e
    except IOError as e:
        raise IOError(
            f"Failed to write file {output_path}: {e}"
        ) from e


# ❌ Ruim
def download_result(self, zip_url: str, filename: str) -> str:
    try:
        response = requests.get(zip_url)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return filename
    except Exception as e:
        print(f"Error: {e}")
        return None
```

### 3. UI Error Handling

```python
# ✅ Bom
def on_upload_failed(self, error_message: str):
    """Handle upload failure with user notification."""
    # Log error
    logger.error(f"Upload failed: {error_message}")

    # Show user-friendly message
    QMessageBox.critical(
        self,
        "Upload Error",
        f"Failed to upload files:\n\n{error_message}\n\n"
        "Please check your internet connection and try again."
    )

    # Restore UI state
    self.add_files_button.setEnabled(True)
    self.process_button.setEnabled(len(self.selected_files) > 0)
    self.progress_bar.setVisible(False)


# ❌ Ruim
def on_upload_failed(self, error_message: str):
    print(error_message)  # User doesn't see this
    # UI state not restored
```

---

## Logging

### 1. Estrutura de Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mineru_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


# ✅ Bom
def upload_batch(self, file_paths: List[str]) -> Dict:
    logger.info(f"Starting upload of {len(file_paths)} files")

    try:
        result = self._do_upload(file_paths)
        logger.info(f"Upload completed: batch_id={result['batch_id']}")
        return result

    except ConnectionError as e:
        logger.error(f"Upload failed due to connection error: {e}")
        raise
    except Exception as e:
        logger.exception("Unexpected error during upload")
        raise


# ❌ Ruim
def upload_batch(self, file_paths: List[str]) -> Dict:
    print(f"Uploading {len(file_paths)} files")  # print instead of logger
    try:
        result = self._do_upload(file_paths)
        return result
    except Exception:
        pass  # Silent failure
```

### 2. Log Levels

```python
# DEBUG: Informação detalhada para diagnóstico
logger.debug(f"Request body: {request_body}")

# INFO: Eventos importantes do fluxo normal
logger.info(f"User {user_id} started processing batch {batch_id}")

# WARNING: Eventos que podem indicar problemas
logger.warning(f"File {filename} not found in API response")

# ERROR: Erros que não param a aplicação
logger.error(f"Failed to download {url}: {error}")

# CRITICAL: Erros críticos que podem parar a aplicação
logger.critical("Failed to connect to database")
```

---

## Configuração

### 1. Separação de Configuração

```python
# ✅ Bom - Separar sensível de não-sensível

# Keyring (sensível)
api_token = keyring.get_password("MinerU", "api_token")

# config.ini (não-sensível)
[Settings]
is_ocr = True
enable_formula = False
language = pt

[Paths]
output_directory = ~/Documents/MinerU_Output


# ❌ Ruim - Tudo em um arquivo de texto
# config.ini
[Settings]
api_token = abc123...  # NUNCA FAÇA ISSO!
is_ocr = True
```

### 2. Defaults Sensatos

```python
# ✅ Bom
class MineruClient:
    def __init__(self):
        self.api_token = None
        self.is_ocr = True  # Default sensato
        self.enable_formula = False
        self.enable_table = True
        self.language = "pt"  # Default para português
        self.model_version = "pipeline"
        self.output_directory = os.path.expanduser("~/Documents/MinerU_Output")
        self.load_config()


# ❌ Ruim
class MineruClient:
    def __init__(self):
        # Sem defaults, vai quebrar se não houver config
        self.api_token = config['api_token']
        self.is_ocr = config['is_ocr']
```

---

## Threading

### 1. QThread Pattern

```python
# ✅ Bom
class Worker(QThread):
    """Worker thread for background operations."""

    # Definir signals
    progress = Signal(int)
    finished = Signal(dict)
    error = Signal(str)

    def __init__(self, data):
        super().__init__()
        self.data = data

    def run(self):
        """Execute em thread separada."""
        try:
            result = self.process_data(self.data)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    def process_data(self, data):
        # Processar dados
        return {}


# Uso
class MainWindow(QMainWindow):
    def start_work(self):
        self.worker = Worker(self.data)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()


# ❌ Ruim
class MainWindow(QMainWindow):
    def start_work(self):
        # Bloqueia UI
        result = self.process_data(self.data)
        self.update_ui(result)
```

### 2. ThreadPoolExecutor Pattern

```python
# ✅ Bom
from concurrent.futures import ThreadPoolExecutor, as_completed

def upload_files_parallel(file_paths: List[str]) -> List[Dict]:
    results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_file = {
            executor.submit(upload_file, path): path
            for path in file_paths
        }

        for future in as_completed(future_to_file):
            file_path = future_to_file[future]
            try:
                result = future.result()
                results.append({"file": file_path, "status": "success"})
            except Exception as e:
                results.append({"file": file_path, "status": "failed", "error": str(e)})

    return results


# ❌ Ruim
def upload_files_sequential(file_paths: List[str]) -> List[Dict]:
    results = []
    for path in file_paths:
        # Lento, sequencial
        result = upload_file(path)
        results.append(result)
    return results
```

---

## Testes

### 1. Estrutura de Teste

```python
# ✅ Bom
import pytest
from unittest.mock import Mock, patch


class TestMineruClient:
    """Testes para MineruClient."""

    @pytest.fixture
    def client(self):
        """Fixture reusável."""
        with patch('keyring.get_password', return_value='test_token'):
            return MineruClient()

    def test_specific_behavior(self, client):
        """Testa comportamento específico."""
        # Arrange
        expected = "value"

        # Act
        result = client.method()

        # Assert
        assert result == expected


# ❌ Ruim
def test_everything():
    """Testa tudo de uma vez."""
    client = MineruClient()
    # Muitas assertions não relacionadas
    assert client.method1() == "a"
    assert client.method2() == "b"
    assert client.method3() == "c"
```

### 2. Mocking

```python
# ✅ Bom
@patch('requests.post')
def test_upload_success(mock_post, client):
    """Testa upload bem-sucedido."""
    # Setup mock
    mock_response = Mock()
    mock_response.json.return_value = {
        'data': {'batch_id': 'batch123', 'file_urls': ['url1']}
    }
    mock_post.return_value = mock_response

    # Test
    with patch('requests.put'):
        result = client.upload_batch(['test.pdf'])

    # Verify
    assert result['batch_id'] == 'batch123'
    mock_post.assert_called_once()


# ❌ Ruim
def test_upload():
    """Testa upload sem mock."""
    client = MineruClient()
    # Faz requisição real
    result = client.upload_batch(['test.pdf'])
    assert result is not None
```

---

## Documentação

### 1. README Structure

```markdown
# Project Name

Brief description

## Features

- Feature 1
- Feature 2

## Installation

Step-by-step guide

## Usage

Examples

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [API](docs/API.md)
- [Contributing](docs/CONTRIBUTING.md)

## License

License info
```

### 2. Code Documentation

```python
# ✅ Bom
class MineruClient:
    """Client for MinerU API operations.

    This class handles all communication with the MinerU service,
    including authentication, file uploads, and result downloads.

    Attributes:
        api_token: Bearer token for authentication
        output_directory: Path for downloaded results

    Example:
        >>> client = MineruClient()
        >>> result = client.upload_batch(['doc.pdf'])
        >>> print(result['batch_id'])
    """

    def upload_batch(self, files: List[str]) -> Dict:
        """Upload batch of files.

        Args:
            files: List of file paths

        Returns:
            Upload result with batch_id

        Raises:
            ValueError: If no files provided
        """
        pass


# ❌ Ruim
class MineruClient:
    # No docstring

    def upload_batch(self, files):
        # Upload files
        pass
```

---

## Anti-Patterns a Evitar

### 1. God Object

```python
# ❌ Evitar
class Application:
    """Faz tudo."""

    def upload_files(self):
        pass

    def download_results(self):
        pass

    def manage_ui(self):
        pass

    def handle_settings(self):
        pass

    def process_data(self):
        pass


# ✅ Preferir separação de responsabilidades
class FileUploader:
    pass

class FileDownloader:
    pass

class UIManager:
    pass
```

### 2. Magic Numbers

```python
# ❌ Evitar
def start_polling(self):
    self.timer.start(10000)  # O que é 10000?


# ✅ Usar constantes nomeadas
POLLING_INTERVAL_MS = 10000  # 10 seconds

def start_polling(self):
    self.timer.start(POLLING_INTERVAL_MS)
```

### 3. Deep Nesting

```python
# ❌ Evitar
def process(data):
    if data:
        if data.valid:
            if data.ready:
                if data.complete:
                    return data.result


# ✅ Early returns
def process(data):
    if not data:
        return None
    if not data.valid:
        return None
    if not data.ready:
        return None
    if not data.complete:
        return None
    return data.result
```

---

## Conclusão

Estes padrões visam:
- **Consistência**: Código uniforme em todo o projeto
- **Manutenibilidade**: Fácil de entender e modificar
- **Testabilidade**: Código testável com mocks/stubs
- **Qualidade**: Menos bugs, mais confiável

Para mais informações, consulte:
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API.md](API.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
