# MinerU Desktop Client - Test Suite Documentation

## Visão Geral

Este documento descreve a estratégia de testes implementada para o MinerU Desktop Client, incluindo testes unitários, de integração e validações.

## Estrutura de Testes

```
tests/
├── __init__.py
├── conftest.py              # Fixtures compartilhadas
├── unit/                    # Testes unitários
│   ├── test_client.py       # Testes do MineruClient
│   ├── test_config.py       # Testes do ConfigManager
│   ├── test_services.py     # Testes dos serviços (Upload/Download)
│   ├── test_validators.py   # Testes de validação
│   └── test_exceptions.py   # Testes de exceções customizadas
├── integration/             # Testes de integração
│   └── test_api_integration.py  # Testes de workflow completo
└── ui/                      # Testes de UI
    └── test_main_window.py  # Testes básicos de UI
```

## Cobertura de Testes

**Cobertura Atual: 80.43%**

### Módulos Testados

| Módulo | Cobertura | Descrição |
|--------|-----------|-----------|
| `core/client.py` | 92.86% | Cliente API MinerU |
| `core/config.py` | 88.60% | Gerenciamento de configuração |
| `core/exceptions.py` | 100% | Exceções customizadas |
| `models/batch.py` | 100% | Modelos de dados |
| `services/upload_service.py` | 100% | Serviço de upload |
| `services/download_service.py` | 100% | Serviço de download |
| `utils/validators.py` | 93.10% | Validadores |

### Módulos Não Testados

Os seguintes módulos não são incluídos nos testes devido à necessidade de GUI:
- `ui/*` - Componentes de interface gráfica (requer Qt display)
- `workers/*` - Workers Qt (requerem Qt display)
- `services/batch_service.py` - Depende fortemente de componentes UI

## Executando os Testes

### Pré-requisitos

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Comandos

#### Executar todos os testes
```bash
pytest tests/
```

#### Executar apenas testes unitários
```bash
pytest tests/unit/ -v
```

#### Executar com cobertura
```bash
pytest tests/ --cov=mineru_desktop --cov-report=html
```

#### Executar testes por marcador
```bash
# Apenas testes unitários
pytest -m unit

# Apenas testes de integração
pytest -m integration

# Excluir testes lentos
pytest -m "not slow"
```

## Tipos de Testes

### Testes Unitários

Testam componentes individuais isoladamente:

- **test_client.py**: Testa todas as operações do `MineruClient` incluindo upload, status check e download
- **test_config.py**: Testa carregamento/salvamento de configurações e integração com keyring
- **test_services.py**: Testa serviços de upload/download e modelos de batch
- **test_validators.py**: Testa todas as funções de validação
- **test_exceptions.py**: Testa hierarquia de exceções

### Testes de Integração

Testam workflows completos com mocks de API:

- Upload → Polling → Download
- Retry logic em uploads
- Tratamento de falhas parciais
- Autenticação
- Progress tracking

### Fixtures

Fixtures compartilhadas em `conftest.py`:

- `temp_dir`: Diretório temporário para testes
- `sample_api_token`: Token de API de teste
- `sample_processing_options`: Opções de processamento padrão
- `sample_batch`: Batch de teste
- `sample_files`: Arquivos PDF de teste
- `mock_batch_response`: Response mockada da API
- `mock_status_response`: Response de status mockada

## Validações Implementadas

### Validação de API Token
- Não pode ser vazio
- Mínimo de 10 caracteres
- Apenas caracteres alfanuméricos, hífens, underscores e pontos

### Validação de Arquivos
- Arquivo deve existir
- Deve ser um arquivo (não diretório)
- Deve ser legível
- Extensão deve ser `.pdf`
- Tamanho máximo configurável

### Validação de Diretórios
- Diretório deve existir ou ser criável
- Deve ter permissão de escrita

### Validação de URLs
- Deve começar com `http://` ou `https://`
- Comprimento mínimo

## Exceções Customizadas

Sistema hierárquico de exceções:

```
MineruException (base)
├── ValidationError
├── AuthenticationError
├── APIError
├── NetworkError
├── ConfigurationError
├── FileOperationError
├── UploadError
├── DownloadError
└── BatchProcessingError
```

Cada exceção pode conter:
- Mensagem de erro
- Exceção original (para stack trace completo)
- Atributos específicos (ex: `status_code` para APIError)

## Configuração de Coverage

O arquivo `.coveragerc` configura:
- Exclusão de código de UI/workers
- Exclusão de linhas padrão (abstractmethod, __main__, etc.)
- Geração de relatórios HTML e XML
- Threshold mínimo de 80%

## Boas Práticas

### Testes Isolados
- Cada teste é independente
- Usa fixtures para setup/teardown
- Não depende de estado global

### Mocks Apropriados
- Chamadas HTTP são mockadas
- Sistema de arquivos usa arquivos temporários
- Keyring é mockado

### Testes Determinísticos
- Sem dependências de tempo real
- Sem acesso a recursos externos
- Resultados consistentes

### Nomenclatura Clara
- `test_<função>_<cenário>_<resultado_esperado>`
- Docstrings descrevem o propósito

## Próximos Passos

Para aumentar ainda mais a cobertura:

1. **Testes de UI com Headless Qt**: Configurar ambiente para testar componentes Qt
2. **Testes de Workers**: Testar threads de upload/polling
3. **Testes de BatchService**: Criar mocks mais elaborados para testar orquestração
4. **Testes E2E**: Testes end-to-end com API de staging

## CI/CD

Exemplo de configuração para GitHub Actions:

```yaml
- name: Run tests
  run: |
    pytest tests/ --cov=mineru_desktop --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v3
  with:
    file: ./coverage.xml
```

## Contato

Para questões sobre testes, consulte a documentação ou abra uma issue no repositório.
