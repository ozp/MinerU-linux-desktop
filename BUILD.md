# Build Instructions

Este documento descreve como construir o MinerU Desktop Client a partir do código fonte.

## Download Direto (Recomendado)

Se você quer apenas usar o aplicativo, baixe o AppImage pronto:

**[Download MinerU-x86_64.AppImage](MinerU-x86_64.AppImage)** (10 MB)

### Como usar o AppImage:

```bash
# 1. Baixe o arquivo
# 2. Torne-o executável
chmod +x MinerU-x86_64.AppImage

# 3. Execute
./MinerU-x86_64.AppImage
```

O AppImage é um executável portátil que funciona em qualquer distribuição Linux sem instalação.

## Construir do Código Fonte

### Pré-requisitos

- Python 3.8+
- pip
- PyInstaller
- appimagetool

### Passos para Build

#### 1. Clone o repositório e instale dependências

```bash
git clone https://github.com/ozp/MinerU-linux-desktop.git
cd MinerU-linux-desktop
pip install -r requirements.txt
pip install pyinstaller
```

#### 2. Build com PyInstaller

```bash
pyinstaller --onefile --windowed --name MinerU \
  --add-data "config.ini.example:." \
  --add-data "mineru_icon.svg:." \
  --hidden-import keyring.backends.SecretService \
  --hidden-import keyring.backends.kwallet \
  main.py
```

Isso criará o executável em `dist/MinerU`.

#### 3. (Opcional) Criar AppImage

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

### PyInstaller não encontra módulos

Se você receber erros sobre módulos não encontrados, adicione-os como hidden imports:

```bash
--hidden-import nome_do_modulo
```

### AppImage não executa

- Verifique se tem permissão de execução: `chmod +x MinerU-x86_64.AppImage`
- Em alguns sistemas, pode ser necessário FUSE: `sudo apt install fuse`

### Executável muito grande

O tamanho do executável (10 MB) é normal e inclui:
- Python runtime
- PySide6 (Qt)
- Todas as dependências
- Recursos do aplicativo

## Informações de Versão

- **Versão**: 1.0.0 MVP
- **PyInstaller**: 6.16.0
- **Python**: 3.11+
- **Qt**: PySide6

## Contribuindo

Para contribuir com melhorias no processo de build, abra um pull request no repositório.
