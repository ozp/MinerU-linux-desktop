# MinerU Linux Desktop Client

Um cliente desktop para a API do MinerU, desenvolvido em Python com PySide6.

## Visão Geral

Este projeto fornece uma interface desktop amigável para o MinerU, permitindo operações eficientes de processamento e mineração de documentos em plataformas Linux.

## Funcionalidades (MVP)

- ✅ Configuração segura de Token da API (via Linux Keyring)
- ✅ Upload de arquivos em lote com validação de tipo
- ✅ Upload paralelo para melhor desempenho (até 5 arquivos simultâneos)
- ✅ Barra de progresso durante uploads
- ✅ Polling automático de status de processamento (a cada 10 segundos)
- ✅ Download automático de resultados para pasta definida pelo usuário
- ✅ Botão para abrir a pasta de saída no gerenciador de arquivos
- ✅ Feedback de progresso em tempo real
- ✅ Tratamento robusto de erros
- ✅ Interface em Português
- ✅ Seleção de modelo (Pipeline ou VLM)
- ✅ Suporte otimizado para português com modelo Pipeline
- ✅ Extração automática de arquivos ZIP após download

## Início Rápido

Para começar a usar o MinerU Desktop, você precisa construir o AppImage localmente:

```bash
# 1. Clone o repositório
git clone https://github.com/ozp/MinerU-linux-desktop.git
cd MinerU-linux-desktop

# 2. Instale as bibliotecas Qt do sistema (apenas uma vez)
./install_system_deps.sh

# 3. Construa o AppImage
./build_appimage.sh

# 4. Execute
./MinerU-x86_64.AppImage
```

O processo de build cria um AppImage portátil (~70 MB) que funciona em **qualquer distribuição Linux**. O AppImage inclui Python e todas as dependências Python.

> **Dica**: Para instruções detalhadas de build, consulte [BUILD.md](BUILD.md).

### Verificando a Versão

Para verificar a versão do aplicativo:
- Abra o aplicativo e vá em **Ajuda > Sobre** no menu
- A versão também é exibida no título da janela

## Requisitos

- Python 3.8 ou superior
- Sistema operacional Linux
- Linux Keyring (geralmente já instalado no sistema)
- **Bibliotecas do sistema** para Qt/PySide6 (veja abaixo)

### Dependências do Sistema

O aplicativo requer bibliotecas Qt específicas do sistema. Para instalá-las:

**Opção 1: Script automático (recomendado)**
```bash
./install_system_deps.sh
```

**Opção 2: Instalação manual**
```bash
apt-get install -y libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 \
    libxcb-shape0 libxcb-xkb1 libxkbcommon-x11-0 libegl1
```

Para mais detalhes sobre as dependências do sistema, consulte [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md).

## Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/ozp/MinerU-linux-desktop.git
cd MinerU-linux-desktop
```

### 2. Instale as dependências do sistema

```bash
./install_system_deps.sh
```

### 3. Crie um ambiente virtual (recomendado)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Instale as dependências Python

```bash
pip install -r requirements.txt
```

## Uso

### 1. Execute a aplicação

```bash
python main.py
```

### 2. Configure suas definições

1. Vá em **Arquivo > Configurações** (ou pressione `Ctrl+,`)
2. Digite seu **Token da API do MinerU**
   - O token é armazenado de forma segura usando o Linux Keyring
   - Nunca é salvo em arquivos de texto
3. Selecione a **Pasta de Saída** onde os resultados serão salvos
4. Configure as **Opções de Processamento**:
   - **Force OCR**: Habilitar OCR para todos os documentos
   - **Enable Formula Recognition**: Detectar e processar fórmulas matemáticas
   - **Enable Table Recognition**: Detectar e processar tabelas
   - **MinerU Model**: Escolha o modelo de processamento
     - **Pipeline (Legado - Melhor para Português)**: Recomendado para documentos em português
     - **VLM (Novo - Sem suporte a idioma)**: Modelo mais recente, mas sem configuração de idioma
   - **Select OCR Language**: Escolha o idioma (Chinês, Inglês, Português)
     - ⚠️ **Nota**: A configuração de idioma está disponível apenas para o modelo Pipeline
5. Clique em **Save**

### 3. Processe documentos

1. Clique em **"Adicionar Arquivos..."**
2. Selecione os arquivos que deseja processar:
   - Documentos: PDF, DOCX, PPTX
   - Imagens: JPG, PNG
3. Clique em **"Iniciar Processamento"**
4. Acompanhe o progresso:
   - A barra de progresso mostra o upload
   - O status de cada arquivo é atualizado automaticamente
   - Downloads acontecem automaticamente quando prontos
   - **Os arquivos são automaticamente extraídos** para pastas individuais
5. Quando concluído, clique em **"Abrir Pasta de Saída"** para ver os resultados
   - Cada documento processado estará em sua própria pasta
   - Exemplo: `documento.pdf` → pasta `documento/` com arquivos markdown, imagens, etc.

## Arquitetura

### Componentes Principais

- **main.py**: Interface gráfica principal (PySide6)
  - `MainWindow`: Janela principal da aplicação
  - `UploadWorker`: Thread worker para uploads não-bloqueantes

- **settings_dialog.py**: Diálogo de configurações
  - Gerenciamento seguro de token via keyring
  - Configuração de pasta de saída
  - Opções de processamento

- **mineru_client.py**: Cliente da API MinerU
  - `upload_batch()`: Upload paralelo com ThreadPoolExecutor
  - `get_batch_status()`: Verificação de status de processamento
  - `download_result()`: Download automático de resultados
  - Tratamento robusto de erros de rede

### Fluxo de Trabalho

```
1. Usuário configura token e pasta de saída
   ↓
2. Usuário seleciona arquivos
   ↓
3. Upload em paralelo (até 5 simultâneos)
   ↓
4. Polling automático a cada 10s
   ↓
5. Download automático quando pronto
   ↓
6. Extração automática de ZIP para pastas
   ↓
7. Notificação ao usuário
```

### Segurança

- **Token da API**: Armazenado com segurança no Linux Keyring
- **config.ini**: Contém APENAS configurações não-sensíveis
- **Nunca versionado**: Token nunca é salvo em arquivos de texto

## Configuração

As configurações são armazenadas em dois locais:

### 1. Linux Keyring (Seguro)
- API Token

### 2. config.ini (Não-sensível)
```ini
[Settings]
is_ocr = True
enable_formula = False
enable_table = True
language = pt
model_version = pipeline

[Paths]
output_directory = ~/Documentos/MinerU_Output
```

## Tipos de Arquivo Suportados

- **Documentos**: .pdf, .docx, .pptx
- **Imagens**: .jpg, .png

## Suporte a Idiomas

### Modelo Pipeline (Recomendado para Português)

O modelo **Pipeline** oferece suporte completo a múltiplos idiomas através do parâmetro `language`:

- ✅ **Português (pt)**: Otimizado para documentos em português brasileiro
- ✅ **Inglês (en)**: Suporte completo
- ✅ **Chinês (ch)**: Suporte completo
- ✅ Outros idiomas suportados pelo [PaddleOCR](https://www.paddleocr.ai/latest/version3.x/algorithm/PP-OCRv5/PP-OCRv5_multi_languages.html)

**Recomendação**: Para documentos em português, utilize sempre o modelo **Pipeline** com o idioma definido como **Português (pt)** para obter os melhores resultados.

### Modelo VLM (Experimental)

O modelo **VLM** é mais recente, mas:

- ⚠️ **Não suporta** configuração de idioma
- ⚠️ Pode ter **dificuldades com texto em português**
- ⚠️ Recomendado apenas para documentos em inglês

**Problema Conhecido**: Textos em português podem aparecer com caracteres corrompidos (ex: "içãç b iv ç c d iibiçãaçãçã") ao usar o modelo VLM.

## Tratamento de Erros

A aplicação inclui tratamento robusto de erros para:

- ✅ Falhas de conexão de rede
- ✅ Timeouts de API
- ✅ Token inválido ou expirado
- ✅ Permissões negadas
- ✅ Falhas de upload de arquivos individuais
- ✅ Falhas de download
- ✅ Pasta de saída inválida

Todas as mensagens de erro são exibidas de forma amigável ao usuário.

## Desenvolvimento

### Estrutura do Projeto

```
MinerU-linux-desktop/
├── main.py                 # Aplicação principal
├── settings_dialog.py      # Diálogo de configurações
├── mineru_client.py        # Cliente da API
├── version.py              # Informações de versão
├── requirements.txt        # Dependências Python
├── config.ini.example      # Exemplo de configuração
├── build_appimage.sh       # Script de build do AppImage
├── release.sh              # Script de release automatizado
├── install_system_deps.sh  # Instalador de dependências do sistema
├── .gitignore             # Arquivos ignorados pelo git
├── README.md              # Esta documentação
├── RELEASE_PROCESS.md     # Documentação do processo de release
├── CHANGELOG.md           # Histórico de mudanças
├── BUILD.md               # Guia de build
├── WORKFLOW.md            # Workflow de desenvolvimento
└── SYSTEM_DEPENDENCIES.md # Documentação de dependências
```

### Dependências

- **PySide6**: Framework de GUI Qt para Python
- **requests**: Cliente HTTP para chamadas de API
- **keyring**: Armazenamento seguro de credenciais

### Versionamento e Releases

O projeto utiliza um sistema de versionamento que garante consistência entre versões e changelog.

#### Criando uma Nova Versão

```bash
# Correção de bugs (1.0.0 → 1.0.1)
./release.sh patch "Descrição das mudanças"

# Nova funcionalidade (1.0.0 → 1.1.0)
./release.sh minor "Descrição das mudanças"

# Breaking changes (1.0.0 → 2.0.0)
./release.sh major "Descrição das mudanças"
```

O script `release.sh` automaticamente:
- ✅ Atualiza a versão em `version.py`
- ✅ Atualiza o CHANGELOG.md
- ✅ Cria commit e tag Git

Para mais detalhes, consulte **[RELEASE_PROCESS.md](RELEASE_PROCESS.md)**.

#### Versionamento

O projeto segue [Semantic Versioning](https://semver.org/lang/pt-BR/):
- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades de forma compatível
- **PATCH**: Correções de bugs compatíveis

A versão é definida centralmente em `version.py` e usada por toda a aplicação.

## Solução de Problemas

### Token não é salvo

- Certifique-se de que o keyring do sistema está funcionando:
  ```bash
  python3 -c "import keyring; print(keyring.get_keyring())"
  ```

### Pasta de saída não abre

- Verifique se a pasta existe e você tem permissões de leitura
- Tente criar manualmente: `mkdir -p ~/Documentos/MinerU_Output`

### Erro de conexão

- Verifique sua conexão com a internet
- Confirme que `https://mineru.net` está acessível
- Verifique se há firewalls ou proxies bloqueando

## Documentação

O projeto inclui documentação detalhada na pasta `docs/`:

### 📚 Documentação Disponível

- **[API.md](docs/API.md)**: Documentação completa da API interna
  - Referência de todas as classes e métodos públicos
  - Exemplos de uso detalhados
  - Estruturas de dados e códigos de erro
  - Guias de uso completo

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)**: Arquitetura do projeto
  - Visão geral da estrutura
  - Padrões de design utilizados
  - Fluxo de dados e comunicação entre componentes

- **[PATTERNS.md](docs/PATTERNS.md)**: Padrões e boas práticas
  - Padrões de código recomendados
  - Tratamento de erros
  - Validação de entrada
  - Logging e debugging

- **[TESTING.md](docs/TESTING.md)**: Guia de testes
  - Como executar os testes
  - Estrutura de testes (unit, integration, UI)
  - Cobertura de código
  - Mocking e fixtures

- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)**: Guia de contribuição
  - Como contribuir para o projeto
  - Padrões de código
  - Processo de revisão de código
  - Configuração do ambiente de desenvolvimento

- **[I18N.md](docs/I18N.md)**: Internacionalização
  - Suporte a múltiplos idiomas
  - Como adicionar novos idiomas
  - Localização da interface

### 💡 Começando com a Documentação

Para desenvolvedores que querem entender o código:
1. Comece com [ARCHITECTURE.md](docs/ARCHITECTURE.md) para visão geral
2. Consulte [API.md](docs/API.md) para detalhes de implementação
3. Veja [PATTERNS.md](docs/PATTERNS.md) para boas práticas

Para contribuidores:
1. Leia [CONTRIBUTING.md](docs/CONTRIBUTING.md) primeiro
2. Configure ambiente de desenvolvimento
3. Consulte [TESTING.md](docs/TESTING.md) antes de fazer mudanças

## Contribuição

Contribuições são bem-vindas! Por favor:

1. Leia o **[Guia de Contribuição](docs/CONTRIBUTING.md)**
2. Fork o repositório
3. Crie uma branch para sua feature
4. Siga os **[Padrões de Código](docs/PATTERNS.md)**
5. Adicione **testes** (veja [TESTING.md](docs/TESTING.md))
6. Commit suas mudanças
7. Push para a branch
8. Abra um Pull Request

## Licença

A determinar.

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do GitHub.
