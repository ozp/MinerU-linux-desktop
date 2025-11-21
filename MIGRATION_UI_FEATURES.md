# Migração de Features de UI Modernas para src/

**Status**: Pendente
**Prioridade**: Alta
**Versão Alvo**: 1.2.0
**Branch**: `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE`

## Contexto

Durante o refactoring de consolidação (v1.1.0), movemos `mineru_desktop/` para `old_code/`, mas essa versão continha **features modernas de UI** que não existem em `src/`. Precisamos migrar essas features antes de mergear na main.

## Features Ausentes em src/

### 1. 🔔 Toast Notifications
**Arquivo**: `old_code/mineru_desktop/ui/toast_notification.py` (169 linhas)
- Widget de notificações não-intrusivas
- Tipos: INFO, SUCCESS, ERROR, WARNING
- Animações de fade in/out
- Posicionamento automático na janela

### 2. 🎨 Theme Switcher (Dark/Light Mode)
**Arquivos de estilo**:
- `old_code/mineru_desktop/ui/styles/dark_theme.qss` (263 linhas)
- `old_code/mineru_desktop/ui/styles/light_theme.qss` (246 linhas)

**Funcionalidades em MainWindow**:
- Menu item: "🌙 Tema Escuro" / "☀️ Tema Claro"
- Método `toggle_theme()` (linha ~545)
- Método `apply_theme()` (linha ~552)
- Salvamento de preferência via ConfigManager

### 3. 📁 Drag & Drop de Arquivos
**Classe**: `FileListWidget` em `old_code/mineru_desktop/ui/main_window.py`
- Herda de QListWidget
- `setAcceptDrops(True)`
- Implementa `dragEnterEvent()`, `dragMoveEvent()`, `dropEvent()`
- Validação de tipos de arquivo durante drag

### 4. 🎨 Material Design Inspired UI
- Botões com ícones aprimorados
- Espaçamento e padding modernos
- Paleta de cores coerente
- Sombras e elevações sutis

## Comparação de Código

```
old_code/mineru_desktop/ui/main_window.py: 625 linhas (COM features)
src/ui/main_window.py:                     468 linhas (SEM features)
Diferença:                                 ~157 linhas de UI moderna
```

## Plano de Migração

### FASE 1: Preparação e Análise

1. **Verificar branch e versão atual**:
   ```bash
   git branch --show-current
   # Deve estar em: claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE

   python3 -c "from version import VERSION; print(VERSION)"
   # Deve mostrar: 1.1.0
   ```

2. **Comparar implementações detalhadamente**:
   ```bash
   # Ver diferenças estruturais
   diff -u src/ui/main_window.py old_code/mineru_desktop/ui/main_window.py | head -100

   # Verificar imports
   grep "^import\|^from" old_code/mineru_desktop/ui/main_window.py | head -20
   grep "^import\|^from" src/ui/main_window.py | head -20
   ```

3. **Identificar dependências**:
   - Toast notifications usa QPropertyAnimation, QGraphicsOpacityEffect
   - Themes usam QFile.readAll() para carregar .qss
   - Drag & drop usa QMimeData, QUrl
   - ConfigManager precisa ter método `get_theme_preference()` e `save_theme_preference()`

### FASE 2: Migração de Arquivos

#### 2.1 Copiar Toast Notification
```bash
cp old_code/mineru_desktop/ui/toast_notification.py src/ui/
```

**Ajustes necessários**:
- Verificar se todos os imports estão corretos para src/
- Adicionar ao `src/ui/__init__.py`:
  ```python
  from .toast_notification import ToastNotification, ToastType
  ```

#### 2.2 Copiar Stylesheets
```bash
mkdir -p src/ui/styles
cp old_code/mineru_desktop/ui/styles/dark_theme.qss src/ui/styles/
cp old_code/mineru_desktop/ui/styles/light_theme.qss src/ui/styles/
```

**Adicionar ao MinerU.spec**:
```python
datas=[
    ('config.ini.example', '.'),
    ('mineru_icon.svg', '.'),
    ('src/ui/styles/*.qss', 'src/ui/styles'),  # ADICIONAR ESTA LINHA
],
```

#### 2.3 Atualizar src/config/config_manager.py

Adicionar métodos para gerenciar preferência de tema:

```python
def get_theme_preference(self) -> str:
    """Get saved theme preference (light/dark)."""
    return self._config.get("UI", "theme", fallback="light")

def save_theme_preference(self, theme: str) -> None:
    """Save theme preference."""
    if "UI" not in self._config:
        self._config.add_section("UI")
    self._config["UI"]["theme"] = theme
    self._save_config()
```

### FASE 3: Integrar Features em src/ui/main_window.py

#### 3.1 Adicionar Drag & Drop

**Localização**: Logo após a definição da classe MainWindow, adicionar classe interna:

```python
class FileListWidget(QListWidget):
    """List widget with drag and drop support for files."""

    def __init__(self, parent=None):
        """Initialize the drag-drop list widget."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.parent_window = parent

    def dragEnterEvent(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):
        """Handle drag move event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """Handle drop event - add files to list."""
        files = [url.toLocalFile() for url in event.mimeData().urls()
                 if url.isLocalFile()]
        if files and self.parent_window:
            for file_path in files:
                self.parent_window.add_file_to_list(file_path)
        event.acceptProposedAction()
```

**Modificar `_create_widgets()`**:
```python
# ANTES:
# self.file_list = QListWidget()

# DEPOIS:
self.file_list = self.FileListWidget(self)
```

#### 3.2 Adicionar Toast Notifications

**Adicionar import no topo**:
```python
from .toast_notification import ToastNotification, ToastType
```

**No `__init__()`, adicionar**:
```python
# Toast notification widget
self.toast = ToastNotification(self)
```

**Modificar métodos de feedback para usar toast**:
- `_on_upload_complete()`: `self.toast.show_success("Upload concluído!")`
- `_on_upload_error()`: `self.toast.show_error(f"Erro: {error_msg}")`
- `_handle_batch_error()`: `self.toast.show_error(f"Erro no processamento")`
- `_on_download_complete()`: `self.toast.show_success("Download concluído!")`

#### 3.3 Adicionar Theme Switcher

**Adicionar atributo no `__init__()`**:
```python
self.current_theme = "light"
```

**No `_create_menu_bar()`, adicionar ao menu View**:
```python
# Theme toggle
self.theme_action = QAction("🌙 Tema Escuro", self)
self.theme_action.triggered.connect(self.toggle_theme)
view_menu.addAction(self.theme_action)
```

**Adicionar métodos no final da classe**:
```python
def toggle_theme(self) -> None:
    """Toggle between light and dark theme."""
    new_theme = "dark" if self.current_theme == "light" else "light"
    self.apply_theme(new_theme)
    self.config.save_theme_preference(new_theme)
    logger.info(f"Theme changed to: {new_theme}")

def apply_theme(self, theme: str) -> None:
    """
    Apply a theme to the application.

    Args:
        theme: Theme name ("light" or "dark")
    """
    self.current_theme = theme

    # Update menu action text
    if theme == "dark":
        self.theme_action.setText("☀️ Tema Claro")
    else:
        self.theme_action.setText("🌙 Tema Escuro")

    # Load stylesheet
    style_path = Path(__file__).parent / "styles" / f"{theme}_theme.qss"
    try:
        with open(style_path, "r", encoding="utf-8") as f:
            stylesheet = f.read()
            self.setStyleSheet(stylesheet)
        logger.info(f"Applied {theme} theme")
    except Exception as e:
        logger.error(f"Failed to load theme {theme}: {e}")
```

**Carregar tema inicial no `__init__()` (após setup da UI)**:
```python
# Apply saved theme preference
saved_theme = self.config.get_theme_preference()
self.apply_theme(saved_theme)
```

### FASE 4: Validação e Testes

#### 4.1 Validar sintaxe Python
```bash
python3 -m py_compile src/ui/main_window.py
python3 -m py_compile src/ui/toast_notification.py
python3 -m py_compile src/config/config_manager.py
```

#### 4.2 Testar imports
```bash
python3 -c "from src.ui import MainWindow, ToastNotification, ToastType; print('✓ Imports OK')"
```

#### 4.3 Executar aplicação (teste visual)
```bash
python3 main.py
```

**Checklist de testes manuais**:
- [ ] Aplicação abre sem erros
- [ ] Drag & drop de PDF funciona
- [ ] Menu "Ver" tem opção de tema
- [ ] Toggle tema dark/light funciona
- [ ] Stylesheet é aplicado corretamente
- [ ] Toast notifications aparecem (testar com erro/sucesso)
- [ ] Preferência de tema é salva ao reiniciar app

#### 4.4 Verificar arquivos na build
```bash
# Verificar que .qss está incluído no spec
grep -A5 "datas=" MinerU.spec
```

### FASE 5: Atualizar Versão e Documentação

#### 5.1 Bumpar versão para 1.2.0
```python
# version.py
VERSION = "1.2.0"
```

#### 5.2 Atualizar CHANGELOG.md

Adicionar entrada de versão 1.2.0:

```markdown
## [1.2.0] - 2025-11-21

### Novas Funcionalidades (UI/UX)
- 🔔 **Toast Notifications**: Notificações não-intrusivas para feedback ao usuário
- 🎨 **Theme Switcher**: Suporte para tema claro e escuro
- 📁 **Drag & Drop**: Arraste arquivos diretamente para a janela
- 🎨 **Material Design**: Interface modernizada com stylesheets customizados

### Arquivos Adicionados
- `src/ui/toast_notification.py` - Sistema de notificações
- `src/ui/styles/dark_theme.qss` - Tema escuro
- `src/ui/styles/light_theme.qss` - Tema claro

### Melhorias de UI
- Feedback visual aprimorado durante operações
- Preferência de tema salva entre sessões
- Interface mais intuitiva e moderna
- Animações suaves para notificações

### Compatibilidade
- ✅ Todas as funcionalidades da v1.1.0 mantidas
- ✅ Configurações existentes compatíveis
- ✅ Build AppImage compatível

## [1.1.0] - 2025-11-21
...
```

Adicionar link no final:
```markdown
[1.2.0]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.2.0
```

#### 5.3 Atualizar main.py docstring (opcional)

Adicionar menção às features de UI moderna:

```python
"""MinerU Linux Desktop Client - Main Entry Point.

...

Features:
    - Modern UI with dark/light theme support
    - Drag & drop file support
    - Toast notifications for user feedback
    - ...
"""
```

### FASE 6: Commit e Push

```bash
git add src/ui/toast_notification.py
git add src/ui/styles/
git add src/ui/main_window.py
git add src/config/config_manager.py
git add version.py
git add CHANGELOG.md
git add MinerU.spec

git status  # Revisar mudanças

git commit -m "feat: Add modern UI features (toast, themes, drag-drop)

Add missing modern UI features from mineru_desktop to src/:

Features Added:
- 🔔 Toast notifications for user feedback
- 🎨 Dark/Light theme switcher with QSS stylesheets
- 📁 Drag & drop file support
- 🎨 Material Design inspired interface

New Files:
- src/ui/toast_notification.py (169 lines)
- src/ui/styles/dark_theme.qss (263 lines)
- src/ui/styles/light_theme.qss (246 lines)

Modified:
- src/ui/main_window.py: +157 lines (UI features)
- src/config/config_manager.py: theme preference methods
- MinerU.spec: include .qss files in build

Version: 1.1.0 → 1.2.0

This completes the UI modernization started in commit d85e754
and ensures all features are preserved in the consolidated codebase."

git push origin claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
```

### FASE 7: Testes Finais e Build

#### 7.1 Build AppImage
```bash
./build_appimage.sh
```

Deve gerar: `MinerU-1.2.0-x86_64.AppImage`

#### 7.2 Testar AppImage
```bash
./MinerU-1.2.0-x86_64.AppImage
```

**Checklist**:
- [ ] Versão 1.2.0 aparece na janela
- [ ] Tema dark/light funciona
- [ ] Drag & drop funciona
- [ ] Toast notifications aparecem

#### 7.3 Limpar old_code (OPCIONAL)

Após confirmar que tudo funciona:
```bash
# Fazer backup local se quiser
tar -czf old_code_backup.tar.gz old_code/

# Remover old_code do repo
git rm -r old_code/
git commit -m "chore: Remove old_code after successful UI migration"
git push
```

### FASE 8: Merge para Main

Quando tudo estiver funcionando:

**Opção A - Via Pull Request (Recomendado)**:
1. Ir para: https://github.com/ozp/MinerU-linux-desktop/pull/new/claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
2. Criar PR com título: "v1.2.0: Consolidação de código + UI moderna"
3. Descrever mudanças no PR
4. Mergear após revisão

**Opção B - Merge direto**:
```bash
# Verificar qual é a branch principal
git branch -r | grep -E "main|master"

# Fazer merge (assumindo main)
git checkout main
git pull origin main
git merge claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
git push origin main

# Criar tag de release
git tag -a v1.2.0 -m "Version 1.2.0: Modern UI + Code consolidation"
git push origin v1.2.0
```

## Checklist Final de Validação

Antes de considerar completo, verificar:

- [ ] Versão é 1.2.0
- [ ] CHANGELOG.md tem entrada 1.2.0 completa
- [ ] Toast notifications funcionam
- [ ] Theme switcher funciona (dark/light)
- [ ] Drag & drop funciona
- [ ] Preferência de tema persiste entre reinicializações
- [ ] AppImage build inclui arquivos .qss
- [ ] AppImage executável mostra v1.2.0
- [ ] Todos os testes manuais de UI passam
- [ ] Sintaxe Python validada (py_compile)
- [ ] Commits pushed para o repositório
- [ ] Ready para merge na main

## Problemas Conhecidos e Soluções

### Problema 1: FileNotFoundError ao carregar .qss
**Solução**: Verificar que styles/ está em `src/ui/styles/` e que MinerU.spec inclui os arquivos:
```python
datas=[
    ('src/ui/styles/*.qss', 'src/ui/styles'),
],
```

### Problema 2: ConfigManager não tem métodos de tema
**Solução**: Adicionar `get_theme_preference()` e `save_theme_preference()` ao ConfigManager

### Problema 3: Toast não aparece
**Solução**: Verificar que `self.toast` é criado APÓS `self.setLayout()` e que o parent está correto

### Problema 4: Drag & drop não funciona
**Solução**: Verificar que `FileListWidget.parent_window` está setado e que método `add_file_to_list()` existe

## Referências

- Commit original de UI moderna: `d85e754` (2025-11-19)
- Branch atual: `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE`
- Código fonte: `old_code/mineru_desktop/ui/`
- Destino: `src/ui/`

## Estimativa de Tempo

- FASE 1-2: 10 minutos (preparação e cópia de arquivos)
- FASE 3: 30 minutos (integração no main_window.py)
- FASE 4-5: 15 minutos (testes e documentação)
- FASE 6-8: 10 minutos (commit, push, merge)

**Total estimado**: ~60-75 minutos

---

**Importante**: Este documento deve ser seguido sequencialmente. Cada fase depende da anterior. Testar frequentemente durante a integração.
