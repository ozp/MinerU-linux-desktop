# Build Instructions

Este documento descreve como construir o MinerU Desktop Client a partir do código fonte.

## Requisitos do Sistema

Antes de construir e executar o AppImage, instale as bibliotecas Qt necessárias:

```bash
# Opção 1: Script automático (recomendado)
./install_system_deps.sh

# Opção 2: Instalação manual
apt-get install -y libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 \
    libxcb-shape0 libxcb-xkb1 libxkbcommon-x11-0 libegl1
```

Para mais detalhes sobre as dependências do sistema, consulte [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md).

## Construir do Código Fonte

### Pré-requisitos

- Python 3.8+
- pip
- PyInstaller
- appimagetool
- cffi (dependência do cryptography)

### Passos para Build

#### Opção 1: Build Automatizado (Recomendado)

Use o script de build automatizado:

```bash
git clone https://github.com/ozp/MinerU-linux-desktop.git
cd MinerU-linux-desktop
./build_appimage.sh
```

Este script irá:
1. Instalar todas as dependências necessárias
2. Construir o executável com PyInstaller
3. Criar a estrutura AppImage
4. Gerar o AppImage final

#### Opção 2: Build Manual

#### 1. Clone o repositório e instale dependências

```bash
git clone https://github.com/ozp/MinerU-linux-desktop.git
cd MinerU-linux-desktop
pip install -r requirements.txt
pip install pyinstaller cffi
```

#### 2. Build com PyInstaller usando o arquivo .spec

```bash
pyinstaller --clean MinerU.spec
```

Isso criará o executável em `dist/MinerU`. O arquivo `MinerU.spec` contém todas as configurações necessárias, incluindo:
- Importações ocultas do PySide6
- Backends do keyring para armazenamento seguro
- Configuração adequada do cryptography
- Dados e recursos do aplicativo

#### 3. Criar AppImage

```bash
# Crie a estrutura AppDir
mkdir -p MinerU.AppDir/usr/bin
mkdir -p MinerU.AppDir/usr/share/icons/hicolor/scalable/apps
mkdir -p MinerU.AppDir/usr/share/applications

# Copie os arquivos
cp dist/MinerU MinerU.AppDir/usr/bin/
cp mineru_icon.svg MinerU.AppDir/
cp mineru_icon.svg MinerU.AppDir/usr/share/icons/hicolor/scalable/apps/
cp MinerU.desktop MinerU.AppDir/
cp MinerU.desktop MinerU.AppDir/usr/share/applications/

# Crie AppRun
cat > MinerU.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/MinerU" "$@"
EOF

chmod +x MinerU.AppDir/AppRun

# Baixe appimagetool
wget https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
chmod +x appimagetool-x86_64.AppImage

# Extraia (se FUSE não estiver disponível)
./appimagetool-x86_64.AppImage --appimage-extract

# Gere o AppImage
ARCH=x86_64 squashfs-root/AppRun --no-appstream MinerU.AppDir MinerU-x86_64.AppImage
```

O AppImage resultante estará em `MinerU-x86_64.AppImage`.

## Estrutura do Build

```
MinerU-linux-desktop/
├── main.py              # Aplicação principal
├── settings_dialog.py   # Diálogo de configurações
├── mineru_client.py     # Cliente da API
├── mineru_icon.svg      # Ícone do aplicativo
├── MinerU.desktop       # Desktop entry
├── MinerU.spec          # Especificação PyInstaller
├── dist/
│   └── MinerU          # Executável standalone
└── MinerU-x86_64.AppImage  # AppImage portátil
```

## Solução de Problemas

### Erro: "Could not load the Qt platform plugin 'xcb'"

Este erro ocorre quando as bibliotecas Qt do sistema estão faltando. Instale-as:

```bash
./install_system_deps.sh
```

Ou manualmente:

```bash
apt-get install -y libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 \
    libxcb-shape0 libxcb-xkb1 libxkbcommon-x11-0 libegl1
```

Para mais informações, consulte [SYSTEM_DEPENDENCIES.md](SYSTEM_DEPENDENCIES.md).

### PyInstaller não encontra módulos

Se você receber erros sobre módulos não encontrados, adicione-os como hidden imports:

```bash
--hidden-import nome_do_modulo
```

### AppImage não executa

- **Primeiro**, verifique se as bibliotecas Qt estão instaladas (veja acima)
- Verifique se tem permissão de execução: `chmod +x MinerU-x86_64.AppImage`
- Em alguns sistemas, pode ser necessário FUSE: `apt install fuse`

### Executável muito grande

O tamanho do executável (~67 MB) é normal e inclui:
- Python runtime
- PySide6 (Qt) e todas suas bibliotecas
- Keyring e backends para armazenamento seguro
- Cryptography e suas dependências
- Requests e outras bibliotecas
- Recursos do aplicativo

**Nota**: As bibliotecas Qt do sistema NÃO estão incluídas e devem ser instaladas separadamente.

## Informações de Versão

- **Versão**: 1.0.0 MVP
- **PyInstaller**: 6.16.0
- **Python**: 3.11+
- **Qt**: PySide6

## Contribuindo

Para contribuir com melhorias no processo de build, abra um pull request no repositório.
