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

## Download Rápido (AppImage)

**Quer começar rapidamente?** Baixe o AppImage pronto para uso:

### 📥 [Download MinerU-x86_64.AppImage](https://github.com/ozp/MinerU-linux-desktop/releases/latest) (~72 MB)

> **Nota sobre Versionamento**: A partir da versão 1.0.0, os AppImages são versionados (ex: `MinerU-1.0.0-x86_64.AppImage`). O link `MinerU-x86_64.AppImage` é um symlink que sempre aponta para a versão mais recente.

**Como usar:**

```bash
# 1. Instale as bibliotecas Qt do sistema (apenas uma vez)
./install_system_deps.sh

# 2. Baixe o arquivo MinerU-x86_64.AppImage (ou versão específica)
# 3. Torne-o executável
chmod +x MinerU-x86_64.AppImage

# 4. Execute
./MinerU-x86_64.AppImage
```

O AppImage é um executável portátil que funciona em **qualquer distribuição Linux**. Inclui Python e todas as dependências Python, mas requer bibliotecas Qt do sistema (instaladas pelo script acima).

### Verificando a Versão

Para verificar a versão do aplicativo instalado:
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

## Documentação

### Documentação Técnica Completa

O projeto inclui documentação técnica abrangente:

- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Arquitetura do sistema e decisões de design
- **[API.md](docs/API.md)** - Documentação completa da API interna
- **[TESTING.md](docs/TESTING.md)** - Guia de testes e como executá-los
- **[CONTRIBUTING.md](docs/CONTRIBUTING.md)** - Como contribuir com o projeto
- **[PATTERNS.md](docs/PATTERNS.md)** - Padrões de código e melhores práticas
- **[I18N.md](docs/I18N.md)** - Sistema de internacionalização

### Documentação de Processo

- **[RELEASE_PROCESS.md](RELEASE_PROCESS.md)** - Processo de release
- **[BUILD.md](BUILD.md)** - Como fazer build do AppImage
- **[WORKFLOW.md](WORKFLOW.md)** - Workflow de desenvolvimento
- **[SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md)** - Dependências do sistema

## Desenvolvimento

### Estrutura do Projeto

```
MinerU-linux-desktop/
├── docs/                       # Documentação técnica
│   ├── ARCHITECTURE.md        # Arquitetura do sistema
│   ├── API.md                 # Documentação da API
│   ├── TESTING.md             # Guia de testes
│   ├── CONTRIBUTING.md        # Guia de contribuição
│   ├── PATTERNS.md            # Padrões de código
│   └── I18N.md                # Internacionalização
├── main.py                    # Aplicação principal
├── settings_dialog.py         # Diálogo de configurações
├── mineru_client.py           # Cliente da API
├── version.py                 # Informações de versão
├── requirements.txt           # Dependências Python
├── config.ini.example         # Exemplo de configuração
├── build_appimage.sh          # Script de build do AppImage
├── release.sh                 # Script de release automatizado
├── install_system_deps.sh     # Instalador de dependências do sistema
├── .gitignore                # Arquivos ignorados pelo git
├── README.md                 # Esta documentação
├── RELEASE_PROCESS.md        # Documentação do processo de release
├── CHANGELOG.md              # Histórico de mudanças
├── BUILD.md                  # Guia de build
├── WORKFLOW.md               # Workflow de desenvolvimento
└── SYSTEM_DEPENDENCIES.md    # Documentação de dependências
```

### Dependências

- **PySide6**: Framework de GUI Qt para Python
- **requests**: Cliente HTTP para chamadas de API
- **keyring**: Armazenamento seguro de credenciais

Veja [ARCHITECTURE.md](docs/ARCHITECTURE.md) para detalhes sobre decisões arquiteturais.

### Sistema de Release Automatizado

Este projeto utiliza um sistema de release automatizado que garante consistência entre versões, README e AppImage.

#### Como Fazer uma Release

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
- ✅ Reconstrói o AppImage com a nova versão
- ✅ Atualiza o CHANGELOG.md
- ✅ Cria commit e tag Git
- ✅ Garante consistência em todos os arquivos

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

## Contribuição

Contribuições são bem-vindas!

**Leia o [Guia de Contribuição](docs/CONTRIBUTING.md)** para detalhes completos sobre:
- Como configurar o ambiente de desenvolvimento
- Padrões de código a seguir
- Processo de pull request
- Como reportar bugs
- Como sugerir melhorias

### Processo Rápido

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/minha-feature`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova feature'`)
4. Push para a branch (`git push origin feature/minha-feature`)
5. Abra um Pull Request

Veja também:
- [PATTERNS.md](docs/PATTERNS.md) - Padrões de código
- [TESTING.md](docs/TESTING.md) - Como escrever e rodar testes

## Licença

A determinar.

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do GitHub.
