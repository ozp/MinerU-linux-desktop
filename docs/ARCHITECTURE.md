# Arquitetura do MinerU Desktop Client

## Visão Geral

O MinerU Desktop Client é uma aplicação desktop desenvolvida em Python usando PySide6 (Qt for Python). A arquitetura segue o padrão Model-View-Controller (MVC) adaptado para aplicações desktop Qt.

## Decisões Arquiteturais

### 1. Framework GUI: PySide6

**Decisão**: Usar PySide6 em vez de alternativas como PyQt5, Tkinter ou Kivy.

**Razões**:
- **Licença**: PySide6 usa LGPL, mais permissiva que PyQt5 (GPL)
- **Nativa**: Aparência nativa em Linux com suporte completo a temas do sistema
- **Moderna**: API moderna e bem documentada
- **Performance**: Excelente performance para operações assíncronas
- **Widgets**: Rico conjunto de widgets profissionais

### 2. Armazenamento Seguro: Linux Keyring

**Decisão**: Usar keyring do sistema para armazenar o token da API.

**Razões**:
- **Segurança**: Tokens nunca são salvos em texto plano
- **Integração**: Usa o sistema de credenciais nativo do Linux (Secret Service API)
- **Simplicidade**: API Python simples e confiável
- **Padrão**: Segue as melhores práticas de segurança

**Alternativas Rejeitadas**:
- Arquivo criptografado: Complexidade adicional de gerenciar chaves
- Variáveis de ambiente: Não persistente entre sessões
- config.ini em texto plano: Inseguro

### 3. Arquitetura de Threading

**Decisão**: Usar QThread para uploads e QTimer para polling.

**Razões**:
- **UI Responsiva**: Operações de rede não bloqueiam a interface
- **Signals/Slots**: Comunicação segura entre threads via sistema Qt
- **Simplicidade**: API QThread é mais simples que threading nativo Python para UI
- **Integração**: QTimer integra-se perfeitamente com o event loop do Qt

**Padrão Implementado**:
```
UI Thread (MainWindow)
    ↓
UploadWorker (QThread) → progress_updated → UI atualiza progress bar
    ↓
    → upload_completed → UI inicia polling
    → upload_failed → UI mostra erro

QTimer (polling)
    ↓ a cada 10s
check_batch_status() → download automático → UI atualizada
```

### 4. Upload Paralelo: ThreadPoolExecutor

**Decisão**: Usar ThreadPoolExecutor para uploads paralelos dentro do worker.

**Razões**:
- **Performance**: Até 5 uploads simultâneos
- **Controle**: Limite configurable de workers
- **Simplicidade**: API de alto nível para paralelismo
- **Robustez**: Tratamento automático de exceções por arquivo

**Configuração**:
```python
with ThreadPoolExecutor(max_workers=5) as executor:
    # Upload paralelo de até 5 arquivos
```

### 5. Estrutura de Configuração

**Decisão**: Separar configurações sensíveis e não-sensíveis.

**Implementação**:
- **Keyring** (sensível):
  - API Token

- **config.ini** (não-sensível):
  - Opções de processamento (OCR, fórmulas, tabelas)
  - Diretório de saída
  - Idioma
  - Versão do modelo

**Benefícios**:
- Segurança: Credenciais nunca em arquivos versionáveis
- Portabilidade: config.ini pode ser compartilhado sem risco
- Flexibilidade: Fácil edição manual de preferências

## Componentes Principais

### 1. main.py

**Responsabilidades**:
- Interface gráfica principal
- Gerenciamento de estado da aplicação
- Coordenação de uploads e polling

**Classes**:

#### MainWindow (QMainWindow)
- **Papel**: Controlador principal da aplicação
- **Responsabilidades**:
  - Gerenciar seleção de arquivos
  - Iniciar/coordenar uploads
  - Polling automático de status
  - Download e extração de resultados
  - Navegação para pasta de saída

**State Machine**:
```
[Idle] → add files → [Files Selected]
  ↓
[Files Selected] → start processing → [Uploading]
  ↓
[Uploading] → upload complete → [Polling]
  ↓
[Polling] → all done → [Completed]
```

#### UploadWorker (QThread)
- **Papel**: Worker assíncrono para uploads
- **Responsabilidades**:
  - Executar upload em background
  - Emitir sinais de progresso
  - Comunicar sucesso/falha

**Signals**:
- `progress_updated(int)`: Progresso 0-100
- `upload_completed(dict)`: Resultado completo
- `upload_failed(str)`: Mensagem de erro

### 2. mineru_client.py

**Responsabilidades**:
- Comunicação com API MinerU
- Tratamento de erros de rede
- Upload paralelo de arquivos

**Classes**:

#### MineruClient
- **Papel**: Cliente HTTP para API REST
- **Responsabilidades**:
  - Autenticação via Bearer token
  - Upload em lote com presigned URLs
  - Verificação de status de processamento
  - Download de resultados

**API Methods**:
```python
upload_batch(files, callback) → {batch_id, uploads}
get_batch_status(batch_id) → {data: {extract_result: [...]}}
download_result(url, filename) → file_path
```

**Fluxo de Upload**:
1. POST `/file-urls/batch` → recebe batch_id e presigned URLs
2. PUT paralelo de arquivos para presigned URLs
3. Retorna resultado agregado

### 3. settings_dialog.py

**Responsabilidades**:
- Configuração de credenciais e preferências
- Validação de entrada
- Persistência de configurações

**Classes**:

#### SettingsDialog (QDialog)
- **Papel**: Interface de configuração
- **Responsabilidades**:
  - Capturar token e preferências
  - Validar entrada do usuário
  - Salvar em keyring e config.ini
  - Habilitar/desabilitar opções baseado no modelo

**Validações**:
- Token não pode ser vazio
- Diretório de saída deve ser especificado
- Cria diretório se não existir

### 4. version.py

**Responsabilidades**:
- Versionamento centralizado
- Informações de versão para UI e build

## Fluxo de Dados

### Fluxo Completo de Processamento

```
1. Usuário seleciona arquivos
   ↓
2. MainWindow.add_files() → selected_files[]
   ↓
3. Usuário clica "Iniciar Processamento"
   ↓
4. MainWindow.start_processing()
   → UploadWorker criado e iniciado
   ↓
5. UploadWorker.run()
   → MineruClient.upload_batch()
     → POST /file-urls/batch (batch_id + URLs)
     → ThreadPoolExecutor: PUT paralelo → presigned URLs
   ↓
6. upload_completed signal
   → MainWindow.on_upload_completed()
     → Atualiza UI
     → Inicia polling (QTimer)
   ↓
7. QTimer a cada 10s
   → MainWindow.check_batch_status()
     → MineruClient.get_batch_status()
     → Para cada arquivo "done":
       → MineruClient.download_result()
       → Extrai ZIP
       → Atualiza UI
   ↓
8. Todos os arquivos processados
   → Para polling
   → Notifica usuário
   → Habilita "Abrir Pasta"
```

## Decisões de UI/UX

### 1. Feedback Visual

**Decisão**: Múltiplos indicadores de progresso e status.

**Implementação**:
- Progress bar durante upload
- Status por arquivo na lista: `[Status] filename`
- Estados: Pronto, Enviado, Processando, Concluído, Falhou

### 2. Polling Automático

**Decisão**: Polling automático em vez de botão manual.

**Razões**:
- Melhor UX: Sem ação do usuário necessária
- Intervalo de 10s: Balanceamento entre responsividade e carga da API
- Download automático: Resultados prontos sem intervenção

### 3. Extração Automática de ZIP

**Decisão**: Extrair automaticamente arquivos ZIP baixados.

**Razões**:
- UX simplificada: Usuário não precisa descompactar manualmente
- Organização: Cada documento em sua própria pasta
- Limpeza: Remove ZIP após extração

**Estrutura**:
```
output_directory/
  ├── documento1/
  │   ├── content.md
  │   └── images/
  ├── documento2/
  │   ├── content.md
  │   └── images/
```

## Tratamento de Erros

### Estratégia Geral

1. **Camada de API** (mineru_client.py):
   - Captura exceções de rede
   - Traduz códigos HTTP em erros significativos
   - Retorna mensagens de erro amigáveis

2. **Camada de UI** (main.py, settings_dialog.py):
   - Exibe erros via QMessageBox
   - Mantém estado consistente mesmo em erro
   - Re-habilita controles após erro

### Tipos de Erro Tratados

| Erro | Camada | Tratamento |
|------|--------|------------|
| Token inválido | API | ValueError com mensagem clara |
| Conexão falhou | API | ConnectionError, sugere verificar internet |
| Timeout | API | TimeoutError, sugere retry |
| Upload falhou | Worker | Signal upload_failed, mostra em UI |
| Arquivo não encontrado | UI | QMessageBox antes de tentar upload |
| Pasta não existe | Settings | Cria automaticamente |

### Código de Exemplo

```python
try:
    response = requests.post(api_url, json=body, headers=headers, timeout=30)
    response.raise_for_status()
except requests.ConnectionError:
    raise ConnectionError("Failed to connect. Check your internet connection.")
except requests.Timeout:
    raise TimeoutError("Request timed out. Try again.")
except requests.HTTPError as e:
    if response.status_code == 401:
        raise ValueError("Invalid API token. Check settings.")
    elif response.status_code == 403:
        raise ValueError("Access forbidden. Verify permissions.")
    else:
        raise Exception(f"API request failed: {e}")
```

## Considerações de Segurança

### 1. Armazenamento de Credenciais

- ✅ Token armazenado em keyring do sistema
- ✅ Nunca logado ou exposto
- ✅ config.ini em .gitignore
- ✅ Exemplo fornecido: config.ini.example

### 2. Validação de Entrada

- ✅ Validação de tipo de arquivo
- ✅ Verificação de existência de arquivo
- ✅ Sanitização de paths
- ✅ Validação de URLs da API

### 3. Comunicação de Rede

- ✅ HTTPS obrigatório (API_BASE_URL usa https://)
- ✅ Bearer token em header
- ✅ Timeouts configurados
- ✅ Validação de resposta

## Performance

### Otimizações Implementadas

1. **Upload Paralelo**:
   - ThreadPoolExecutor com 5 workers
   - ~5x mais rápido que upload sequencial

2. **Threading Não-Bloqueante**:
   - UI permanece responsiva
   - QThread para operações longas

3. **Streaming de Download**:
   ```python
   response.get(url, stream=True)
   for chunk in response.iter_content(chunk_size=8192):
       f.write(chunk)
   ```

4. **Polling Inteligente**:
   - Para automaticamente quando completo
   - Timer cleanup adequado

### Métricas Típicas

- Upload de 5 PDFs (~2MB cada): ~10-15s
- Polling interval: 10s
- Download + extração: ~2-5s por arquivo

## Extensibilidade

### Pontos de Extensão

1. **Novos Tipos de Arquivo**:
   - Adicionar em `QFileDialog.setNameFilter()`
   - API MinerU precisa suportar

2. **Novos Modelos de Processamento**:
   - Adicionar em `SettingsDialog.model_combo`
   - Ajustar `get_processing_options()`

3. **Novos Idiomas**:
   - Adicionar em `SettingsDialog.language_combo`
   - Verificar suporte PaddleOCR

4. **Múltiplos Backends**:
   - Abstrair `MineruClient` em interface
   - Implementar diferentes backends

## Dependências

### Dependências Principais

```
PySide6 >= 6.0.0         # Framework GUI
requests >= 2.28.0       # Cliente HTTP
keyring >= 23.0.0        # Armazenamento seguro
```

### Dependências do Sistema

```
libxcb-cursor0           # Qt XCB plugin
libxcb-icccm4           # Qt XCB plugin
libxcb-keysyms1         # Qt XCB plugin
libxcb-shape0           # Qt XCB plugin
libxcb-xkb1             # Qt XCB plugin
libxkbcommon-x11-0      # Qt keyboard
libegl1                 # OpenGL support
```

### Gráfico de Dependências

```
MinerU Desktop Client
├── PySide6
│   ├── Qt6 Core
│   ├── Qt6 Widgets
│   └── Qt6 GUI
├── requests
│   └── urllib3
├── keyring
│   └── SecretStorage (Linux)
└── Python stdlib
    ├── configparser
    ├── os
    ├── sys
    ├── zipfile
    └── concurrent.futures
```

## Diagrama de Componentes

```
┌─────────────────────────────────────────────────────┐
│                   MainWindow (UI)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ File List    │  │ Progress Bar │  │ Buttons   │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────┬────────────────────────────────────────┘
             │
             ├─ signals/slots ──→ UploadWorker (QThread)
             │                          ↓
             │                    upload_batch()
             │                          ↓
             ├──────────────→ MineruClient (API)
             │                    ↓         ↓
             │              POST /batch  PUT /s3
             │
             └─ QTimer ──→ check_batch_status()
                              ↓
                        GET /batch/:id
                              ↓
                        download_result()
                              ↓
                        extract ZIP

┌─────────────────────────────────────────────────────┐
│              SettingsDialog (Config)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │
│  │ API Token    │  │ Checkboxes   │  │ Dropdowns │ │
│  └──────────────┘  └──────────────┘  └───────────┘ │
└────────────┬────────────────────────────────────────┘
             │
             ├──→ Linux Keyring (token)
             └──→ config.ini (settings)
```

## Padrões de Design Utilizados

### 1. Observer Pattern
- **Onde**: Signals/Slots do Qt
- **Uso**: Comunicação entre UI e workers

### 2. Worker Pattern
- **Onde**: UploadWorker
- **Uso**: Operações assíncronas

### 3. Singleton (Implícito)
- **Onde**: MainWindow
- **Uso**: Uma única janela principal

### 4. Strategy Pattern (Parcial)
- **Onde**: Seleção de modelo (Pipeline vs VLM)
- **Uso**: Diferentes estratégias de processamento

## Próximas Evoluções Sugeridas

### Curto Prazo
1. ✅ Internacionalização (i18n) completa
2. ✅ Testes unitários
3. Sistema de logging estruturado
4. Retry automático em falhas de rede

### Médio Prazo
1. Suporte a drag-and-drop de arquivos
2. Histórico de processamentos
3. Configurações por perfil
4. Notificações do sistema

### Longo Prazo
1. Processamento local opcional
2. Integração com cloud storage
3. Batch scheduling
4. Plugin system

## Referências

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [Qt Threading Basics](https://doc.qt.io/qt-6/thread-basics.html)
- [Python keyring](https://pypi.org/project/keyring/)
- [MinerU API Documentation](https://mineru.net/api/docs)
- [Semantic Versioning](https://semver.org/)
