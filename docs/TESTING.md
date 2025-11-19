# Guia de Testes - MinerU Desktop Client

Este documento descreve como executar testes, criar novos testes e validar o comportamento da aplicação.

## Índice

- [Visão Geral](#visão-geral)
- [Configuração do Ambiente de Testes](#configuração-do-ambiente-de-testes)
- [Executando Testes](#executando-testes)
- [Tipos de Testes](#tipos-de-testes)
- [Escrevendo Novos Testes](#escrevendo-novos-testes)
- [Testes Manuais](#testes-manuais)
- [CI/CD](#cicd)

---

## Visão Geral

O projeto utiliza as seguintes ferramentas de teste:

- **pytest**: Framework de testes principal
- **pytest-qt**: Plugin para testes de PySide6
- **unittest.mock**: Para mocking de dependências
- **coverage**: Para análise de cobertura de código

### Status Atual

> **Nota**: Este projeto está em desenvolvimento inicial. O framework de testes está sendo implementado.

---

## Configuração do Ambiente de Testes

### 1. Instalar Dependências de Teste

```bash
# Ativar ambiente virtual
source venv/bin/activate

# Instalar dependências de teste
pip install pytest pytest-qt pytest-cov pytest-mock
```

### 2. Estrutura de Diretórios de Teste

```
MinerU-linux-desktop/
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartilhadas
│   ├── test_mineru_client.py    # Testes do cliente API
│   ├── test_main.py              # Testes da UI principal
│   ├── test_settings_dialog.py  # Testes do diálogo de settings
│   ├── test_version.py          # Testes de versioning
│   └── fixtures/                # Arquivos de teste
│       ├── sample.pdf
│       ├── sample.docx
│       └── sample_response.json
```

### 3. Arquivo de Configuração pytest

Criar `pytest.ini` na raiz do projeto:

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Unit tests
    integration: Integration tests
    ui: UI tests
    slow: Slow running tests
```

---

## Executando Testes

### Executar Todos os Testes

```bash
pytest
```

### Executar Testes Específicos

```bash
# Por arquivo
pytest tests/test_mineru_client.py

# Por classe
pytest tests/test_mineru_client.py::TestMineruClient

# Por função
pytest tests/test_mineru_client.py::TestMineruClient::test_upload_batch
```

### Executar por Marcador

```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de UI
pytest -m ui

# Excluir testes lentos
pytest -m "not slow"
```

### Com Cobertura

```bash
# Cobertura básica
pytest --cov

# Cobertura com relatório HTML
pytest --cov --cov-report=html

# Ver relatório
open htmlcov/index.html
```

### Modo Verbose

```bash
# Mais detalhes
pytest -v

# Ainda mais detalhes
pytest -vv

# Mostrar print statements
pytest -s
```

### Executar em Paralelo

```bash
# Instalar pytest-xdist
pip install pytest-xdist

# Executar em múltiplos cores
pytest -n auto
```

---

## Tipos de Testes

### 1. Testes Unitários

Testam componentes individuais isoladamente.

**Exemplo**: `tests/test_mineru_client.py`

```python
import pytest
from unittest.mock import Mock, patch
from mineru_client import MineruClient


class TestMineruClient:
    """Testes unitários para MineruClient."""

    @pytest.fixture
    def client(self):
        """Fixture que retorna cliente configurado."""
        with patch('keyring.get_password', return_value='test_token'):
            return MineruClient()

    def test_get_headers_with_token(self, client):
        """Testa que headers incluem token de autorização."""
        headers = client.get_headers()
        assert 'Authorization' in headers
        assert headers['Authorization'] == 'Bearer test_token'

    def test_get_headers_without_token(self):
        """Testa exceção quando token não está configurado."""
        with patch('keyring.get_password', return_value=None):
            client = MineruClient()
            with pytest.raises(ValueError, match="API token not configured"):
                client.get_headers()

    def test_get_processing_options_pipeline(self, client):
        """Testa opções de processamento para modelo pipeline."""
        client.model_version = 'pipeline'
        client.language = 'pt'
        options = client.get_processing_options()

        assert options['model_version'] == 'pipeline'
        assert options['language'] == 'pt'
        assert 'enable_formula' in options
        assert 'enable_table' in options

    def test_get_processing_options_vlm(self, client):
        """Testa que VLM não inclui parâmetro language."""
        client.model_version = 'vlm'
        options = client.get_processing_options()

        assert options['model_version'] == 'vlm'
        assert 'language' not in options

    @patch('requests.post')
    def test_upload_batch_success(self, mock_post, client, tmp_path):
        """Testa upload em lote bem-sucedido."""
        # Criar arquivo de teste
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        # Mock da resposta da API
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'batch_id': 'batch123',
                'file_urls': ['https://s3.../upload']
            }
        }
        mock_post.return_value = mock_response

        # Mock do PUT para presigned URL
        with patch('requests.put') as mock_put:
            mock_put.return_value = Mock()
            result = client.upload_batch([str(test_file)])

        assert result['batch_id'] == 'batch123'
        assert len(result['uploads']) == 1
        assert result['uploads'][0]['status'] == 'success'

    @patch('requests.post')
    def test_upload_batch_connection_error(self, mock_post, client):
        """Testa tratamento de erro de conexão."""
        mock_post.side_effect = requests.ConnectionError()

        with pytest.raises(ConnectionError, match="Failed to connect"):
            client.upload_batch(['test.pdf'])

    @patch('requests.get')
    def test_get_batch_status(self, mock_get, client):
        """Testa obtenção de status de lote."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'batch_id': 'batch123',
                'extract_result': [
                    {
                        'file_name': 'test.pdf',
                        'state': 'done',
                        'full_zip_url': 'https://s3.../result.zip'
                    }
                ]
            }
        }
        mock_get.return_value = mock_response

        status = client.get_batch_status('batch123')

        assert status['data']['batch_id'] == 'batch123'
        assert len(status['data']['extract_result']) == 1
        assert status['data']['extract_result'][0]['state'] == 'done'
```

### 2. Testes de Integração

Testam interação entre componentes.

**Exemplo**: `tests/test_integration.py`

```python
import pytest
from unittest.mock import patch, Mock
from PySide6.QtWidgets import QApplication
from main import MainWindow
from mineru_client import MineruClient


class TestIntegration:
    """Testes de integração."""

    @pytest.fixture
    def app(self, qtbot):
        """Fixture da aplicação Qt."""
        return QApplication.instance() or QApplication([])

    @pytest.fixture
    def window(self, qtbot):
        """Fixture da janela principal."""
        with patch('keyring.get_password', return_value='test_token'):
            window = MainWindow()
            qtbot.addWidget(window)
            return window

    def test_add_files_updates_ui(self, window, qtbot, tmp_path):
        """Testa que adicionar arquivos atualiza a UI."""
        # Criar arquivo de teste
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf")

        # Mock do diálogo de arquivos
        with patch('PySide6.QtWidgets.QFileDialog.selectedFiles',
                   return_value=[str(test_file)]):
            window.add_files()

        # Verificar que arquivo foi adicionado
        assert len(window.selected_files) == 1
        assert window.file_list.count() == 1
        assert window.process_button.isEnabled()

    @patch('requests.post')
    @patch('requests.put')
    def test_full_upload_workflow(self, mock_put, mock_post, window, qtbot, tmp_path):
        """Testa fluxo completo de upload."""
        # Setup
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf")

        mock_response = Mock()
        mock_response.json.return_value = {
            'data': {
                'batch_id': 'batch123',
                'file_urls': ['https://s3.../upload']
            }
        }
        mock_post.return_value = mock_response
        mock_put.return_value = Mock()

        # Adicionar arquivo
        window.selected_files = [str(test_file)]

        # Iniciar processamento
        window.start_processing()

        # Aguardar worker completar
        qtbot.waitUntil(lambda: window.current_batch_id is not None, timeout=5000)

        # Verificar
        assert window.current_batch_id == 'batch123'
        assert window.polling_timer is not None
```

### 3. Testes de UI

Testam interface gráfica e interações do usuário.

**Exemplo**: `tests/test_ui.py`

```python
import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication
from unittest.mock import patch
from settings_dialog import SettingsDialog


class TestSettingsDialog:
    """Testes de UI do diálogo de settings."""

    @pytest.fixture
    def dialog(self, qtbot):
        """Fixture do diálogo."""
        with patch('keyring.get_password', return_value=None):
            dialog = SettingsDialog()
            qtbot.addWidget(dialog)
            return dialog

    def test_empty_token_shows_warning(self, dialog, qtbot):
        """Testa que token vazio mostra warning."""
        dialog.token_input.setText('')

        with patch('PySide6.QtWidgets.QMessageBox.warning') as mock_warning:
            dialog.save_settings()
            mock_warning.assert_called_once()

    def test_model_change_disables_language(self, dialog, qtbot):
        """Testa que modelo VLM desabilita seleção de idioma."""
        # Selecionar VLM
        vlm_index = dialog.model_combo.findData('vlm')
        dialog.model_combo.setCurrentIndex(vlm_index)

        # Verificar que language está desabilitado
        assert not dialog.language_combo.isEnabled()
        assert not dialog.language_label.isEnabled()

    def test_model_change_enables_language(self, dialog, qtbot):
        """Testa que modelo Pipeline habilita seleção de idioma."""
        # Selecionar Pipeline
        pipeline_index = dialog.model_combo.findData('pipeline')
        dialog.model_combo.setCurrentIndex(pipeline_index)

        # Verificar que language está habilitado
        assert dialog.language_combo.isEnabled()
        assert dialog.language_label.isEnabled()

    def test_folder_selection(self, dialog, qtbot, tmp_path):
        """Testa seleção de pasta de saída."""
        test_dir = tmp_path / "output"
        test_dir.mkdir()

        with patch('PySide6.QtWidgets.QFileDialog.getExistingDirectory',
                   return_value=str(test_dir)):
            dialog.select_output_folder()

        assert dialog.output_path_input.text() == str(test_dir)
```

### 4. Testes End-to-End

Testam fluxo completo da aplicação.

**Exemplo**: `tests/test_e2e.py`

```python
import pytest
import time
from unittest.mock import patch, Mock
from PySide6.QtCore import Qt


class TestE2E:
    """Testes end-to-end."""

    @pytest.fixture
    def setup_app(self, qtbot, tmp_path):
        """Setup completo da aplicação."""
        # Mock keyring
        with patch('keyring.get_password', return_value='test_token'):
            from main import MainWindow
            window = MainWindow()
            qtbot.addWidget(window)

            # Configurar output directory
            window.mineru_client.output_directory = str(tmp_path)

            return window, tmp_path

    @patch('requests.post')
    @patch('requests.put')
    @patch('requests.get')
    def test_complete_workflow(self, mock_get, mock_put, mock_post,
                               setup_app, qtbot, tmp_path):
        """Testa workflow completo: upload → polling → download."""
        window, output_dir = setup_app

        # Criar arquivo de teste
        test_file = tmp_path / "test.pdf"
        test_file.write_bytes(b"fake pdf content")

        # Mock upload
        upload_response = Mock()
        upload_response.json.return_value = {
            'data': {
                'batch_id': 'batch123',
                'file_urls': ['https://s3.../upload']
            }
        }
        mock_post.return_value = upload_response
        mock_put.return_value = Mock()

        # Mock status (inicialmente processing, depois done)
        status_responses = [
            {
                'data': {
                    'extract_result': [{
                        'file_name': 'test.pdf',
                        'state': 'processing'
                    }]
                }
            },
            {
                'data': {
                    'extract_result': [{
                        'file_name': 'test.pdf',
                        'state': 'done',
                        'full_zip_url': 'https://s3.../result.zip'
                    }]
                }
            }
        ]
        mock_get.side_effect = [Mock(json=lambda: r) for r in status_responses]

        # Mock download
        with patch('requests.get') as mock_download:
            mock_download.return_value = Mock(
                iter_content=lambda chunk_size: [b'fake zip']
            )

            # Adicionar arquivo
            window.selected_files = [str(test_file)]
            window.add_files()

            # Iniciar processamento
            window.start_processing()

            # Aguardar upload
            qtbot.waitUntil(lambda: window.current_batch_id is not None,
                           timeout=5000)

            # Simular polling
            window.check_batch_status()  # processing
            window.check_batch_status()  # done, trigger download

            # Verificar resultado
            assert window.open_folder_button.isEnabled()
```

---

## Escrevendo Novos Testes

### Estrutura Básica

```python
import pytest
from unittest.mock import Mock, patch


class TestMyFeature:
    """Testes para MyFeature."""

    @pytest.fixture
    def setup(self):
        """Setup comum para testes."""
        # Setup code
        yield  # Retorna controle para o teste
        # Teardown code

    def test_something(self, setup):
        """Testa algo específico."""
        # Arrange
        # ... preparar dados

        # Act
        # ... executar ação

        # Assert
        # ... verificar resultado
        assert True
```

### Fixtures Úteis

```python
# conftest.py
import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """QApplication para todos os testes."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def mock_keyring():
    """Mock do keyring."""
    with patch('keyring.get_password', return_value='test_token'), \
         patch('keyring.set_password'):
        yield


@pytest.fixture
def mock_api():
    """Mock de chamadas de API."""
    with patch('requests.post') as mock_post, \
         patch('requests.get') as mock_get, \
         patch('requests.put') as mock_put:
        yield {
            'post': mock_post,
            'get': mock_get,
            'put': mock_put
        }


@pytest.fixture
def sample_pdf(tmp_path):
    """Cria PDF de amostra."""
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake content")
    return pdf_path
```

### Melhores Práticas

1. **Um conceito por teste**
   ```python
   # ✅ Bom
   def test_upload_with_valid_token():
       pass

   def test_upload_with_invalid_token():
       pass

   # ❌ Ruim
   def test_upload():
       # Testa válido e inválido no mesmo teste
       pass
   ```

2. **Nomes descritivos**
   ```python
   # ✅ Bom
   def test_upload_batch_raises_error_when_no_files_provided():
       pass

   # ❌ Ruim
   def test_upload():
       pass
   ```

3. **Arrange-Act-Assert**
   ```python
   def test_get_headers():
       # Arrange
       client = MineruClient()
       client.api_token = 'test123'

       # Act
       headers = client.get_headers()

       # Assert
       assert headers['Authorization'] == 'Bearer test123'
   ```

4. **Usar fixtures para setup**
   ```python
   @pytest.fixture
   def configured_client():
       client = MineruClient()
       client.api_token = 'test123'
       return client

   def test_something(configured_client):
       # Cliente já configurado
       result = configured_client.do_something()
       assert result is not None
   ```

---

## Testes Manuais

### Checklist de Testes Manuais

#### Instalação e Configuração

- [ ] Instalar dependências do sistema
- [ ] Criar e ativar venv
- [ ] Instalar dependências Python
- [ ] Executar aplicação pela primeira vez

#### Configurações

- [ ] Abrir diálogo de settings
- [ ] Inserir token API
- [ ] Selecionar diretório de saída
- [ ] Alterar opções de processamento
- [ ] Alternar entre modelos Pipeline e VLM
- [ ] Verificar que idioma é desabilitado para VLM
- [ ] Salvar e verificar persistência

#### Upload de Arquivos

- [ ] Adicionar arquivo único
- [ ] Adicionar múltiplos arquivos
- [ ] Tentar adicionar arquivo duplicado
- [ ] Remover arquivo da lista
- [ ] Tentar processar sem arquivos
- [ ] Processar com token inválido
- [ ] Processar com token válido

#### Processamento

- [ ] Verificar progress bar durante upload
- [ ] Verificar status de arquivos na lista
- [ ] Aguardar polling automático
- [ ] Verificar transição de estados
- [ ] Verificar download automático
- [ ] Verificar extração de ZIP

#### Resultados

- [ ] Abrir pasta de saída
- [ ] Verificar estrutura de diretórios
- [ ] Verificar conteúdo extraído
- [ ] Processar múltiplos lotes

#### Erros

- [ ] Testar sem conexão de internet
- [ ] Testar com token inválido
- [ ] Testar timeout (arquivo muito grande?)
- [ ] Testar pasta de saída sem permissão

#### UI/UX

- [ ] Verificar responsividade durante operações
- [ ] Testar atalhos de teclado (Ctrl+,, Ctrl+Q)
- [ ] Verificar diálogo About
- [ ] Fechar aplicação durante upload
- [ ] Fechar aplicação durante polling

### Template de Relatório de Bug

```markdown
## Bug Report

**Descrição**:
[Descrição clara e concisa do bug]

**Passos para Reproduzir**:
1.
2.
3.

**Comportamento Esperado**:
[O que deveria acontecer]

**Comportamento Atual**:
[O que está acontecendo]

**Screenshots**:
[Se aplicável]

**Ambiente**:
- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.10.12]
- Versão da aplicação: [e.g., 1.0.1]

**Logs/Traceback**:
```
[Cole aqui]
```

**Informações Adicionais**:
[Contexto adicional]
```

---

## CI/CD

### GitHub Actions

Criar `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        python-version: ['3.8', '3.9', '3.10', '3.11']

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y libxcb-cursor0 libxcb-icccm4 \
          libxcb-keysyms1 libxcb-shape0 libxcb-xkb1 \
          libxkbcommon-x11-0 libegl1 xvfb

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-qt pytest-cov pytest-mock

    - name: Run tests
      run: |
        xvfb-run pytest --cov --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

### Pre-commit Hooks

Criar `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: pytest
        name: pytest
        entry: pytest
        language: system
        pass_filenames: false
        always_run: true
```

Instalar:

```bash
pip install pre-commit
pre-commit install
```

---

## Métricas de Qualidade

### Objetivos de Cobertura

- **Mínimo**: 70% de cobertura geral
- **Objetivo**: 85% de cobertura geral
- **Crítico**: 95% para `mineru_client.py`

### Verificar Cobertura

```bash
pytest --cov --cov-report=term-missing

# Ver áreas não cobertas
pytest --cov --cov-report=html
open htmlcov/index.html
```

---

## Troubleshooting

### Testes de UI Falhando

```bash
# Executar com Xvfb (headless)
xvfb-run pytest tests/test_ui.py
```

### Import Errors

```bash
# Adicionar diretório ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Testes Lentos

```bash
# Identificar testes lentos
pytest --durations=10

# Marcar como slow
@pytest.mark.slow
def test_heavy_operation():
    pass

# Pular testes lentos
pytest -m "not slow"
```

---

## Recursos Adicionais

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-qt Documentation](https://pytest-qt.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py](https://coverage.readthedocs.io/)

---

## Próximos Passos

1. ✅ Implementar testes unitários para `mineru_client.py`
2. ✅ Implementar testes de UI para `settings_dialog.py`
3. ✅ Implementar testes de integração
4. Configurar CI/CD no GitHub Actions
5. Adicionar badges de coverage no README
6. Implementar testes E2E automatizados
