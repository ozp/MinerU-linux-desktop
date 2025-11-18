#!/bin/bash
set -e

echo "=========================================="
echo "MinerU Desktop Client - AppImage Builder"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Extract version from version.py
VERSION=$(python3 -c "import sys; sys.path.insert(0, '.'); from version import VERSION; print(VERSION)")
echo -e "${GREEN}Building version: ${VERSION}${NC}"
echo ""

# Check if running in a virtual environment (recommended)
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo -e "${YELLOW}Warning: Not running in a virtual environment.${NC}"
    echo "It's recommended to use a virtual environment:"
    echo "  python3 -m venv venv"
    echo "  source venv/bin/activate"
    echo ""
fi

# Step 1: Install dependencies
echo -e "${GREEN}[1/6] Installing Python dependencies...${NC}"
pip install -q -r requirements.txt
pip install -q pyinstaller

# Step 2: Clean previous builds
echo -e "${GREEN}[2/6] Cleaning previous builds...${NC}"
rm -rf build/ dist/ MinerU.AppDir/ MinerU-*.AppImage

# Step 3: Build with PyInstaller
echo -e "${GREEN}[3/6] Building with PyInstaller...${NC}"
pyinstaller --clean MinerU.spec

# Verify the executable was created
if [ ! -f "dist/MinerU" ]; then
    echo -e "${RED}Error: PyInstaller build failed - executable not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ PyInstaller build successful${NC}"

# Step 4: Create AppImage structure
echo -e "${GREEN}[4/6] Creating AppImage structure...${NC}"
mkdir -p MinerU.AppDir/usr/bin
mkdir -p MinerU.AppDir/usr/share/icons/hicolor/scalable/apps
mkdir -p MinerU.AppDir/usr/share/applications

# Copy files
cp dist/MinerU MinerU.AppDir/usr/bin/
cp mineru_icon.svg MinerU.AppDir/
cp mineru_icon.svg MinerU.AppDir/usr/share/icons/hicolor/scalable/apps/
cp MinerU.desktop MinerU.AppDir/
cp MinerU.desktop MinerU.AppDir/usr/share/applications/

# Create AppRun script
cat > MinerU.AppDir/AppRun << 'EOF'
#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}
export PATH="${HERE}/usr/bin:${PATH}"
export LD_LIBRARY_PATH="${HERE}/usr/lib:${LD_LIBRARY_PATH}"
exec "${HERE}/usr/bin/MinerU" "$@"
EOF

chmod +x MinerU.AppDir/AppRun

# Step 5: Download appimagetool if needed
if [ ! -f "appimagetool-x86_64.AppImage" ]; then
    echo -e "${GREEN}[5/6] Downloading appimagetool...${NC}"
    wget -q --show-progress https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Extract appimagetool (for systems without FUSE)
if [ ! -d "squashfs-root" ]; then
    echo -e "${GREEN}Extracting appimagetool...${NC}"
    ./appimagetool-x86_64.AppImage --appimage-extract > /dev/null 2>&1
fi

# Step 6: Generate the AppImage
echo -e "${GREEN}[6/6] Generating AppImage...${NC}"
APPIMAGE_NAME="MinerU-${VERSION}-x86_64.AppImage"
ARCH=x86_64 squashfs-root/AppRun --no-appstream MinerU.AppDir "${APPIMAGE_NAME}"

# Verify the AppImage was created
if [ ! -f "${APPIMAGE_NAME}" ]; then
    echo -e "${RED}Error: AppImage creation failed${NC}"
    exit 1
fi

# Make it executable
chmod +x "${APPIMAGE_NAME}"

# Create a symlink for convenience (always points to latest)
ln -sf "${APPIMAGE_NAME}" MinerU-x86_64.AppImage

# Display results
echo ""
echo -e "${GREEN}=========================================="
echo "Build completed successfully!"
echo "==========================================${NC}"
echo ""
echo "AppImage created: ${APPIMAGE_NAME}"
ls -lh "${APPIMAGE_NAME}"
echo ""
echo "Symlink created: MinerU-x86_64.AppImage -> ${APPIMAGE_NAME}"
echo ""
echo "To run the application:"
echo ""
echo -e "${YELLOW}IMPORTANT: First-time users must install Qt system libraries:${NC}"
echo "  ./install_system_deps.sh"
echo ""
echo "Then run the application:"
echo "  ./${APPIMAGE_NAME}"
echo "  or"
echo "  ./MinerU-x86_64.AppImage"
echo ""
echo "For more information, see SYSTEM_DEPENDENCIES.md"
echo ""
