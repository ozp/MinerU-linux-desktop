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

## Download Rápido (AppImage)

**Quer começar rapidamente?** Baixe o AppImage pronto para uso:

### 📥 [Download MinerU-x86_64.AppImage](MinerU-x86_64.AppImage) (10 MB)

**Como usar:**

```bash
# 1. Instale as bibliotecas Qt do sistema (apenas uma vez)
./install_system_deps.sh

# 2. Baixe o arquivo MinerU-x86_64.AppImage
# 3. Torne-o executável
chmod +x MinerU-x86_64.AppImage

# 4. Execute
./MinerU-x86_64.AppImage
```

O AppImage é um executável portátil que funciona em **qualquer distribuição Linux**. Inclui Python e todas as dependências Python, mas requer bibliotecas Qt do sistema (instaladas pelo script acima).

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
   - **Select OCR Language**: Escolha o idioma (Chinês, Inglês, Português)
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
5. Quando concluído, clique em **"Abrir Pasta de Saída"** para ver os resultados

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
6. Notificação ao usuário
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

[Paths]
output_directory = ~/Documentos/MinerU_Output
```

## Tipos de Arquivo Suportados

- **Documentos**: .pdf, .docx, .pptx
- **Imagens**: .jpg, .png

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
├── requirements.txt        # Dependências Python
├── config.ini.example      # Exemplo de configuração
├── .gitignore             # Arquivos ignorados pelo git
└── README.md              # Esta documentação
```

### Dependências

- **PySide6**: Framework de GUI Qt para Python
- **requests**: Cliente HTTP para chamadas de API
- **keyring**: Armazenamento seguro de credenciais

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

Contribuições são bem-vindas! Por favor:

1. Fork o repositório
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

A determinar.

## Suporte

Para problemas ou dúvidas, abra uma issue no repositório do GitHub.
