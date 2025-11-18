#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=========================================="
echo "MinerU Desktop Client - Release Manager"
echo "==========================================${NC}"
echo ""

# Function to display usage
usage() {
    echo "Usage: $0 <version_type> [description]"
    echo ""
    echo "Version types:"
    echo "  major    - Incrementa versão major (1.0.0 -> 2.0.0)"
    echo "  minor    - Incrementa versão minor (1.0.0 -> 1.1.0)"
    echo "  patch    - Incrementa versão patch (1.0.0 -> 1.0.1)"
    echo "  custom   - Define versão customizada (requer argumento adicional)"
    echo ""
    echo "Description: Descrição breve das mudanças (opcional mas recomendado)"
    echo ""
    echo "Exemplos:"
    echo "  $0 patch \"Correção de bugs na interface\""
    echo "  $0 minor \"Nova funcionalidade de exportação\""
    echo "  $0 custom 2.0.0 \"Grande atualização com breaking changes\""
    exit 1
}

# Check arguments
if [ $# -lt 1 ]; then
    usage
fi

VERSION_TYPE=$1
DESCRIPTION="${2:-Release automático}"

# Extract current version
CURRENT_VERSION=$(python3 -c "import sys; sys.path.insert(0, '.'); from version import VERSION; print(VERSION)")
echo -e "${GREEN}Versão atual: ${CURRENT_VERSION}${NC}"

# Calculate new version
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"

case $VERSION_TYPE in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
        ;;
    patch)
        PATCH=$((PATCH + 1))
        NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"
        ;;
    custom)
        if [ $# -lt 2 ]; then
            echo -e "${RED}Erro: Versão customizada requer número de versão${NC}"
            usage
        fi
        NEW_VERSION=$2
        DESCRIPTION="${3:-Release customizado}"
        ;;
    *)
        echo -e "${RED}Erro: Tipo de versão inválido: ${VERSION_TYPE}${NC}"
        usage
        ;;
esac

echo -e "${GREEN}Nova versão: ${NEW_VERSION}${NC}"
echo -e "${YELLOW}Descrição: ${DESCRIPTION}${NC}"
echo ""

# Confirmation
read -p "Continuar com a release? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Release cancelada.${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}[1/6] Atualizando version.py...${NC}"
# Update version.py
sed -i "s/VERSION = \".*\"/VERSION = \"${NEW_VERSION}\"/" version.py
echo -e "${GREEN}✓ version.py atualizado${NC}"

echo ""
echo -e "${BLUE}[2/6] Construindo novo AppImage...${NC}"
# Build new AppImage
./build_appimage.sh
echo -e "${GREEN}✓ AppImage construído: MinerU-${NEW_VERSION}-x86_64.AppImage${NC}"

echo ""
echo -e "${BLUE}[3/6] Atualizando CHANGELOG...${NC}"
# Create CHANGELOG.md if it doesn't exist
if [ ! -f CHANGELOG.md ]; then
    cat > CHANGELOG.md << 'EOF'
# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

EOF
fi

# Add new version to CHANGELOG
TODAY=$(date +%Y-%m-%d)
# Create temporary file with new entry
cat > /tmp/changelog_entry.txt << EOF

## [${NEW_VERSION}] - ${TODAY}

### Descrição
${DESCRIPTION}

### Mudanças
- AppImage atualizado para versão ${NEW_VERSION}
- README atualizado com informações da versão ${NEW_VERSION}

EOF

# Insert after the header (line 7)
sed -i "7r /tmp/changelog_entry.txt" CHANGELOG.md
rm /tmp/changelog_entry.txt
echo -e "${GREEN}✓ CHANGELOG.md atualizado${NC}"

echo ""
echo -e "${BLUE}[4/6] Atualizando README.md...${NC}"
# Update README with new version info
# This is already handled automatically by the version.py system
echo -e "${GREEN}✓ README atualizado (automático via version.py)${NC}"

echo ""
echo -e "${BLUE}[5/6] Criando commit...${NC}"
# Git operations
git add version.py CHANGELOG.md README.md MinerU-${NEW_VERSION}-x86_64.AppImage MinerU-x86_64.AppImage
git commit -m "Release version ${NEW_VERSION}

${DESCRIPTION}

- Versão atualizada para ${NEW_VERSION}
- AppImage reconstruído
- CHANGELOG atualizado
"
echo -e "${GREEN}✓ Commit criado${NC}"

echo ""
echo -e "${BLUE}[6/6] Criando tag...${NC}"
git tag -a "v${NEW_VERSION}" -m "Version ${NEW_VERSION}

${DESCRIPTION}
"
echo -e "${GREEN}✓ Tag v${NEW_VERSION} criada${NC}"

echo ""
echo -e "${GREEN}=========================================="
echo "Release ${NEW_VERSION} concluída com sucesso!"
echo "==========================================${NC}"
echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo "1. Revisar as mudanças: git log -1 -p"
echo "2. Fazer push do commit: git push origin $(git branch --show-current)"
echo "3. Fazer push da tag: git push origin v${NEW_VERSION}"
echo ""
echo -e "${BLUE}Ou fazer push de tudo de uma vez:${NC}"
echo "git push origin $(git branch --show-current) && git push origin v${NEW_VERSION}"
echo ""
echo -e "${GREEN}Arquivos criados:${NC}"
echo "- MinerU-${NEW_VERSION}-x86_64.AppImage"
echo "- MinerU-x86_64.AppImage (symlink)"
echo ""
