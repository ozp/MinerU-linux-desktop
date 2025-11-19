# API Interna - MinerU Desktop Client

Esta documentação descreve a API interna do MinerU Desktop Client, incluindo todas as classes públicas, métodos e suas interfaces.

## Índice

- [MineruClient](#mineruclient)
- [MainWindow](#mainwindow)
- [UploadWorker](#uploadworker)
- [SettingsDialog](#settingsdialog)
- [Version](#version)

---

## MineruClient

Cliente para interação com a API REST do MinerU.

**Localização**: `mineru_client.py`

### Constantes de Classe

```python
CONFIG_FILE = "config.ini"
KEYRING_SERVICE = "MinerU"
KEYRING_USERNAME = "api_token"
API_BASE_URL = "https://mineru.net/api/v4"
```

### Construtor

```python
def __init__(self) -> None
```

Inicializa o cliente com configuração padrão e carrega configurações do keyring e arquivo.

**Efeitos Colaterais**:
- Carrega token do keyring
- Lê config.ini se existir
- Define valores padrão se não houver configuração

### Métodos Públicos

#### load_config()

```python
def load_config(self) -> None
```

Carrega configuração do keyring e arquivo config.ini.

**Configurações Carregadas**:
- `api_token`: Do keyring (seguro)
- `is_ocr`: bool - Forçar OCR
- `enable_formula`: bool - Reconhecimento de fórmulas
- `enable_table`: bool - Reconhecimento de tabelas
- `language`: str - Idioma OCR (pt, en, ch)
- `model_version`: str - Modelo (pipeline, vlm)
- `output_directory`: str - Diretório de saída

**Exemplo**:
```python
client = MineruClient()
client.load_config()  # Recarrega após mudança de configuração
```

#### get_headers()

```python
def get_headers(self) -> Dict[str, str]
```

Retorna headers HTTP com token de autorização.

**Retorna**:
- `dict`: Headers incluindo `Authorization: Bearer <token>`

**Exceções**:
- `ValueError`: Se token não estiver configurado

**Exemplo**:
```python
headers = client.get_headers()
# {'Authorization': 'Bearer abc123...'}
```

#### get_processing_options()

```python
def get_processing_options(self) -> Dict[str, any]
```

Retorna opções de processamento atuais para parâmetros em nível de lote.

**Retorna**:
- `dict`: Opções de configuração
  - `enable_formula`: bool
  - `enable_table`: bool
  - `model_version`: str
  - `language`: str (apenas para modelo pipeline)

**Nota**: `is_ocr` não é incluído pois deve ser definido por arquivo.

**Exemplo**:
```python
options = client.get_processing_options()
# {
#   'enable_formula': False,
#   'enable_table': True,
#   'model_version': 'pipeline',
#   'language': 'pt'
# }
```

#### upload_batch()

```python
def upload_batch(
    self,
    file_paths: List[str],
    progress_callback: Optional[Callable[[int], None]] = None
) -> Dict
```

Faz upload de lote de arquivos para API MinerU com uploads paralelos.

**Processo em Duas Etapas**:
1. POST request para obter batch_id e presigned URLs
2. PUT requests paralelos para upload dos arquivos

**Parâmetros**:
- `file_paths`: Lista de caminhos de arquivos locais
- `progress_callback`: Função callback opcional para atualizações de progresso (0-100)

**Retorna**:
- `dict`: Resposta contendo:
  - `batch_id`: str - ID do lote
  - `uploads`: List[dict] - Status de cada upload
    - `file`: str - Nome do arquivo
    - `status`: str - "success" ou "failed"
    - `error`: str - Mensagem de erro (se failed)

**Exceções**:
- `ValueError`: Se token não configurado ou nenhum arquivo fornecido
- `ConnectionError`: Falha de conexão com API
- `TimeoutError`: Request timeout
- `requests.HTTPError`: Erros HTTP específicos (401, 403, etc.)

**Exemplo**:
```python
def update_progress(percent):
    print(f"Progress: {percent}%")

result = client.upload_batch(
    ['doc1.pdf', 'doc2.pdf'],
    progress_callback=update_progress
)

print(f"Batch ID: {result['batch_id']}")
for upload in result['uploads']:
    print(f"{upload['file']}: {upload['status']}")
```

**Comportamento de Upload Paralelo**:
- Máximo de 5 uploads simultâneos
- ThreadPoolExecutor gerencia paralelismo
- Callback de progresso chamado após cada arquivo completar

#### get_batch_status()

```python
def get_batch_status(self, batch_id: str) -> Dict
```

Obtém status de processamento de um lote.

**Parâmetros**:
- `batch_id`: ID do lote a verificar

**Retorna**:
- `dict`: Informação de status para todos os arquivos do lote
  ```python
  {
    'data': {
      'batch_id': str,
      'extract_result': [
        {
          'file_name': str,
          'state': str,  # 'pending', 'processing', 'done', 'failed'
          'err_msg': str,  # Se failed
          'full_zip_url': str  # Se done
        },
        ...
      ]
    }
  }
  ```

**Exceções**:
- `ValueError`: Token inválido ou batch_id não encontrado
- `ConnectionError`: Falha de conexão
- `TimeoutError`: Request timeout

**Exemplo**:
```python
status = client.get_batch_status('batch_abc123')
for file_info in status['data']['extract_result']:
    print(f"{file_info['file_name']}: {file_info['state']}")
```

#### download_result()

```python
def download_result(self, zip_url: str, filename: str) -> str
```

Faz download de arquivo de resultado da URL fornecida.

**Parâmetros**:
- `zip_url`: URL para download do arquivo ZIP
- `filename`: Nome para o arquivo baixado

**Retorna**:
- `str`: Caminho completo do arquivo baixado

**Efeitos Colaterais**:
- Cria `output_directory` se não existir
- Salva arquivo no diretório de saída

**Exceções**:
- `ConnectionError`: Falha no download
- `TimeoutError`: Download timeout

**Exemplo**:
```python
zip_path = client.download_result(
    'https://s3.../result.zip',
    'doc1_result.zip'
)
print(f"Downloaded to: {zip_path}")
# /home/user/Documents/MinerU_Output/doc1_result.zip
```

---

## MainWindow

Janela principal da aplicação.

**Localização**: `main.py`

### Construtor

```python
def __init__(self) -> None
```

Inicializa a janela principal e componentes.

**Atributos Inicializados**:
- `selected_files`: List[str] - Arquivos selecionados
- `current_batch_id`: Optional[str] - ID do lote atual
- `mineru_client`: MineruClient - Cliente API
- `upload_worker`: Optional[UploadWorker] - Worker de upload
- `polling_timer`: Optional[QTimer] - Timer de polling
- `file_status_map`: Dict[str, str] - Map de status de arquivos

### Métodos Públicos

#### setup_ui()

```python
def setup_ui(self) -> None
```

Configura componentes da interface do usuário.

Cria e organiza todos os elementos da UI incluindo menu bar, controles de seleção de arquivos, indicadores de progresso e botões.

#### create_menu_bar()

```python
def create_menu_bar(self) -> None
```

Cria menu bar com menus File e Help.

**Menus**:
- **File**:
  - Settings (Ctrl+,)
  - Exit (Ctrl+Q)
- **Help**:
  - About

#### open_settings()

```python
def open_settings(self) -> None
```

Abre diálogo de configurações.

Recarrega configuração do cliente se settings forem salvos com sucesso.

#### show_about()

```python
def show_about(self) -> None
```

Mostra diálogo About com informações de versão e features.

#### add_files()

```python
def add_files(self) -> None
```

Abre diálogo de seleção de arquivos.

**Comportamento**:
- Permite seleção múltipla
- Filtra por tipos suportados (PDF, DOCX, PPTX, JPG, PNG)
- Previne duplicatas
- Atualiza lista de arquivos e status map
- Habilita botão de processar se houver arquivos

#### remove_selected_files()

```python
def remove_selected_files(self) -> None
```

Remove arquivos selecionados da lista de processamento.

**Comportamento**:
- Remove de `selected_files`
- Remove de `file_status_map`
- Atualiza widget de lista
- Desabilita botão processar se lista ficar vazia

#### start_processing()

```python
def start_processing(self) -> None
```

Inicia processamento de arquivos selecionados via upload em background.

**Comportamento**:
- Valida que há arquivos selecionados
- Desabilita controles durante upload
- Cria e inicia UploadWorker
- Mostra progress bar
- Conecta signals do worker

**Mostra Warning Se**: Nenhum arquivo selecionado

#### on_upload_progress(progress: int)

```python
def on_upload_progress(self, progress: int) -> None
```

Atualiza progress bar durante upload.

**Parâmetros**:
- `progress`: Porcentagem de progresso (0-100)

#### on_upload_completed(result: dict)

```python
def on_upload_completed(self, result: dict) -> None
```

Trata conclusão de upload bem-sucedido.

**Parâmetros**:
- `result`: Resultado do upload
  - `batch_id`: str
  - `uploads`: List[dict]

**Comportamento**:
- Armazena batch_id
- Atualiza status dos arquivos na UI
- Mostra mensagem de sucesso/falha
- Inicia polling automático se algum upload teve sucesso

#### on_upload_failed(error_message: str)

```python
def on_upload_failed(self, error_message: str) -> None
```

Trata falha de upload com notificação ao usuário.

**Parâmetros**:
- `error_message`: Descrição do erro

**Comportamento**:
- Mostra diálogo de erro
- Re-habilita controles UI

#### start_polling()

```python
def start_polling(self) -> None
```

Inicia polling automático de status.

**Comportamento**:
- Cria QTimer que verifica status a cada 10 segundos
- Faz verificação imediata ao iniciar
- Limpa timer existente antes de criar novo

#### check_batch_status()

```python
def check_batch_status(self) -> None
```

Verifica status do lote atual e baixa arquivos completos.

**Comportamento**:
- Consulta API para status atual
- Atualiza status dos arquivos na UI
- Baixa e extrai resultados completos automaticamente
- Continua polling até todos os arquivos atingirem estado final
- Habilita botão "Abrir Pasta" quando pelo menos um arquivo completa
- Para polling quando todos os arquivos estiverem finalizados

**Estados de Arquivo**:
- `pending`: Na fila
- `processing`: Em processamento
- `done`: Completo (trigger download)
- `failed`: Falhou

#### update_file_status(filename: str, status: str)

```python
def update_file_status(self, filename: str, status: str) -> None
```

Atualiza status de arquivo no widget de lista.

**Parâmetros**:
- `filename`: Nome do arquivo
- `status`: Novo texto de status

#### open_output_folder()

```python
def open_output_folder(self) -> None
```

Abre diretório de saída no gerenciador de arquivos do sistema.

**Comportamento**:
- Usa QDesktopServices para abrir pasta
- Mostra warning se diretório não existe

#### closeEvent(event: QCloseEvent)

```python
def closeEvent(self, event: QCloseEvent) -> None
```

Trata evento de fechamento da aplicação com cleanup adequado.

**Parâmetros**:
- `event`: Evento de fechamento

**Comportamento**:
- Para timer de polling ativo
- Aguarda thread de upload worker completar
- Aceita evento de fechamento

---

## UploadWorker

Worker thread para uploads de arquivos.

**Localização**: `main.py`

### Signals

```python
progress_updated = Signal(int)      # Progresso 0-100
upload_completed = Signal(dict)     # Resultado completo
upload_failed = Signal(str)         # Mensagem de erro
```

### Construtor

```python
def __init__(self, mineru_client: MineruClient, file_paths: List[str]) -> None
```

**Parâmetros**:
- `mineru_client`: Instância do cliente API
- `file_paths`: Lista de caminhos de arquivos para upload

### Métodos

#### run()

```python
def run(self) -> None
```

Executa operação de upload em thread separada.

**Comportamento**:
- Roda em background
- Comunica via signals
- Trata exceções
- Emite signals apropriados baseado no resultado

**Emits**:
- `progress_updated`: Durante upload com porcentagem
- `upload_completed`: Em sucesso com dict de resultado
- `upload_failed`: Em erro com string de mensagem

**Exemplo de Uso**:
```python
worker = UploadWorker(client, ['file1.pdf', 'file2.pdf'])
worker.progress_updated.connect(on_progress)
worker.upload_completed.connect(on_complete)
worker.upload_failed.connect(on_error)
worker.start()
```

---

## SettingsDialog

Diálogo para configuração de settings API e opções de processamento.

**Localização**: `settings_dialog.py`

### Constantes de Classe

```python
CONFIG_FILE = "config.ini"
KEYRING_SERVICE = "MinerU"
KEYRING_USERNAME = "api_token"
```

### Construtor

```python
def __init__(self, parent: Optional[QWidget] = None) -> None
```

**Parâmetros**:
- `parent`: Widget pai (opcional)

**Comportamento**:
- Configura UI
- Carrega settings existentes

### Métodos Públicos

#### setup_ui()

```python
def setup_ui(self) -> None
```

Configura componentes da interface do usuário.

Cria e organiza todos os elementos incluindo input de token API, seletor de diretório de saída, checkboxes de opções de processamento e dropdowns de seleção de modelo/idioma.

#### select_output_folder()

```python
def select_output_folder(self) -> None
```

Abre diálogo de seleção de diretório.

Atualiza campo de input com diretório selecionado.

#### on_model_changed()

```python
def on_model_changed(self) -> None
```

Trata mudança de seleção de modelo.

**Comportamento**:
- Habilita/desabilita seletor de idioma baseado no modelo
- Modelo Pipeline: Suporta configuração de idioma
- Modelo VLM: Não suporta idioma
- Ajusta estilo de mensagem de warning

#### load_settings()

```python
def load_settings(self) -> None
```

Carrega settings do keyring e arquivo config.

**Fontes**:
- Keyring: API token
- config.ini: Outras configurações

**Defaults** (se não houver config):
- Output directory: `~/Documents/MinerU_Output`
- Force OCR: True
- Enable formula: False
- Enable table: True
- Language: Portuguese (pt)
- Model: Pipeline

#### save_settings()

```python
def save_settings(self) -> None
```

Salva settings para keyring e arquivo config.

**Validações**:
- Token não pode ser vazio
- Diretório de saída deve ser especificado

**Comportamento**:
- Salva token para keyring
- Cria diretório de saída se não existir
- Escreve settings não-sensíveis para config.ini
- Mostra diálogo de sucesso/erro

**Settings Salvos em config.ini**:
```ini
[Settings]
is_ocr = True
enable_formula = False
enable_table = True
language = pt
model_version = pipeline

[Paths]
output_directory = ~/Documents/MinerU_Output
```

---

## Version

Informações de versão da aplicação.

**Localização**: `version.py`

### Constantes

```python
VERSION = "1.0.1"
VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = VERSION.split(".")
VERSION_STRING = f"MinerU Desktop Client v{VERSION}"
VERSION_SHORT = VERSION
```

### Funções

#### get_version()

```python
def get_version() -> str
```

Retorna string de versão atual.

**Retorna**: `"1.0.1"`

#### get_version_string()

```python
def get_version_string() -> str
```

Retorna string de versão completa para display.

**Retorna**: `"MinerU Desktop Client v1.0.1"`

#### get_version_info()

```python
def get_version_info() -> dict
```

Retorna informações de versão como dicionário.

**Retorna**:
```python
{
    "version": "1.0.1",
    "major": "1",
    "minor": "0",
    "patch": "1",
    "string": "MinerU Desktop Client v1.0.1"
}
```

---

## Estruturas de Dados Comuns

### Upload Result

```python
{
    "batch_id": str,
    "uploads": [
        {
            "file": str,
            "status": "success" | "failed",
            "error": str  # Opcional, presente se status == "failed"
        }
    ]
}
```

### Batch Status Response

```python
{
    "data": {
        "batch_id": str,
        "extract_result": [
            {
                "file_name": str,
                "state": "pending" | "processing" | "done" | "failed",
                "err_msg": str,  # Se state == "failed"
                "full_zip_url": str  # Se state == "done"
            }
        ]
    }
}
```

### Configuration File Format

```ini
[Settings]
is_ocr = True
enable_formula = False
enable_table = True
language = pt
model_version = pipeline

[Paths]
output_directory = ~/Documents/MinerU_Output
```

---

## Códigos de Erro

### ValueError

Lançado quando:
- Token API não está configurado
- Token API é inválido (HTTP 401)
- Acesso proibido (HTTP 403)
- Nenhum arquivo fornecido para upload
- Resposta API inválida (faltando batch_id ou file_urls)
- Contagem de URL não corresponde à contagem de arquivos
- Batch ID não encontrado (HTTP 404)

### ConnectionError

Lançado quando:
- Falha na conexão com API MinerU
- Falha no download de arquivo

### TimeoutError

Lançado quando:
- Request para API MinerU timeout
- Download timeout

### Exception (genérico)

Lançado quando:
- Falha em request API com código de status inesperado
- Falha no download com erro inesperado

---

## Exemplos de Uso Completos

### Exemplo 1: Upload e Monitoramento Básico

```python
from mineru_client import MineruClient

# Inicializar cliente
client = MineruClient()

# Upload de arquivos
result = client.upload_batch(['doc1.pdf', 'doc2.pdf'])
batch_id = result['batch_id']

print(f"Batch ID: {batch_id}")
for upload in result['uploads']:
    print(f"{upload['file']}: {upload['status']}")

# Verificar status
status = client.get_batch_status(batch_id)
for file_info in status['data']['extract_result']:
    state = file_info['state']
    filename = file_info['file_name']
    print(f"{filename}: {state}")

    # Download se pronto
    if state == 'done':
        zip_url = file_info['full_zip_url']
        output_name = f"{filename}_result.zip"
        zip_path = client.download_result(zip_url, output_name)
        print(f"Downloaded: {zip_path}")
```

### Exemplo 2: Upload com Progress Callback

```python
from mineru_client import MineruClient

def show_progress(percent):
    print(f"Upload Progress: {percent}%")

client = MineruClient()
result = client.upload_batch(
    ['large1.pdf', 'large2.pdf', 'large3.pdf'],
    progress_callback=show_progress
)

print(f"Upload complete! Batch ID: {result['batch_id']}")
```

### Exemplo 3: Configuração Programática

```python
import configparser
import keyring

# Salvar token no keyring
keyring.set_password("MinerU", "api_token", "your_token_here")

# Criar config.ini
config = configparser.ConfigParser()
config['Settings'] = {
    'is_ocr': 'True',
    'enable_formula': 'False',
    'enable_table': 'True',
    'language': 'pt',
    'model_version': 'pipeline'
}
config['Paths'] = {
    'output_directory': '~/Documents/MinerU_Output'
}

with open('config.ini', 'w') as f:
    config.write(f)

# Cliente agora carregará estas configurações
from mineru_client import MineruClient
client = MineruClient()
```

### Exemplo 4: Tratamento de Erros

```python
from mineru_client import MineruClient

client = MineruClient()

try:
    result = client.upload_batch(['doc.pdf'])
except ValueError as e:
    print(f"Configuration error: {e}")
    # Abrir settings dialog
except ConnectionError as e:
    print(f"Network error: {e}")
    # Mostrar mensagem para verificar internet
except TimeoutError as e:
    print(f"Timeout: {e}")
    # Sugerir retry
except Exception as e:
    print(f"Unexpected error: {e}")
    # Log e reportar
```

---

## Notas de Implementação

### Thread Safety

- `MineruClient` **não é thread-safe**
- Criar instâncias separadas para threads diferentes
- Ou usar locks para proteger acesso compartilhado

### Performance

- Upload paralelo usa até 5 workers
- Arquivos grandes podem levar vários minutos
- Progress callback é chamado após cada arquivo (não durante)
- Polling interval é 10 segundos (hard-coded)

### Segurança

- Tokens são armazenados em keyring do sistema
- Nunca logados ou impressos
- HTTPS usado para todas as comunicações
- config.ini não deve ser versionado

### Limitações

- Upload paralelo fixado em 5 workers
- Polling interval fixado em 10s
- Sem suporte a cancelamento de upload
- Sem retry automático em falhas de rede
- Sem persistência de estado entre execuções

---

## Changelog da API

### v1.0.1
- Adicionadas docstrings detalhadas
- Melhor tratamento de erros
- Documentação de API completa

### v1.0.0
- Release inicial
- Upload em lote com paralelismo
- Polling automático
- Download e extração de resultados
