# 📋 Documento de Migração - UI Features Modernas
## MinerU Desktop Client - Versão 1.1.0 → 1.2.0

---

## 📌 CONTEXTO

Durante o refactoring major da versão 1.1.0 (commit e6bcb83), consolidamos a base de código de ~4.000 linhas duplicadas para uma arquitetura SOLID unificada em `src/`.

**Problema identificado:** No processo de consolidação, algumas **features modernas de UI** que estavam implementadas no código antigo (`old_code/mineru_desktop/ui/main_window.py`) **não foram migradas** para a nova implementação (`src/ui/main_window.py`).

### 📊 Comparação de Código

| Arquivo | Linhas | Status |
|---------|--------|--------|
| `old_code/mineru_desktop/ui/main_window.py` | **625** | 🟢 Features completas |
| `src/ui/main_window.py` | **468** | 🟡 Features básicas |
| **Diferença** | **-157 linhas** | ⚠️ Features perdidas |

---

## 🚨 FEATURES PERDIDAS

### 1️⃣ **Toast Notifications** (Notificações não-intrusivas)
- ❌ Classe `ToastNotification` não migrada
- ❌ Enum `ToastType` (INFO, SUCCESS, ERROR, WARNING)
- ❌ Animações de fade in/out
- ❌ Posicionamento automático na janela
- 📁 Arquivo original: `old_code/mineru_desktop/ui/toast_notification.py` (170 linhas)

### 2️⃣ **Drag & Drop de Arquivos**
- ❌ Classe `DragDropListWidget` não migrada
- ❌ Método `dragEnterEvent()`
- ❌ Método `dragMoveEvent()`
- ❌ Método `dropEvent()`
- ❌ Integração com `add_files_from_paths()`

### 3️⃣ **Theme Switcher (Dark/Light Mode)**
- ❌ Menu "Visualizar" com toggle de tema
- ❌ Método `toggle_theme()`
- ❌ Método `apply_theme(theme: str)`
- ❌ Suporte para carregar arquivos `.qss`
- ❌ Persistência de preferência de tema
- 📁 Arquivos de tema:
  - `old_code/mineru_desktop/ui/styles/dark_theme.qss` (264 linhas)
  - `old_code/mineru_desktop/ui/styles/light_theme.qss` (247 linhas)

### 4️⃣ **ConfigManager - Métodos de Tema**
- ❌ `get_theme_preference()` → Carrega tema do config.ini
- ❌ `save_theme_preference(theme)` → Salva tema no config.ini

### 5️⃣ **Emojis nos Botões (UX Moderna)**
- ⚠️ Poucos emojis na versão atual vs. versão antiga com emojis consistentes

---

## 🎯 PLANO DE MIGRAÇÃO - 8 FASES

**Tempo estimado:** 60-75 minutos
**Versão alvo:** 1.2.0
**Branch de trabalho:** `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE`

---

## ✅ FASE 1: Preparação e Análise

### 1.1 Verificar estrutura atual
```bash
# Verificar branch atual
git status
git branch

# Verificar versão atual
cat version.py

# Listar estrutura de src/
tree src/ -L 2

# Verificar se stylesheets existem
ls -la src/ui/styles/ 2>/dev/null || echo "Pasta styles/ não existe"
```

### 1.2 Criar estrutura de pastas
```bash
# Criar pasta de styles se não existir
mkdir -p src/ui/styles
```

### 1.3 Backup de segurança
```bash
# Criar backup do main_window.py atual
cp src/ui/main_window.py src/ui/main_window.py.backup

# Verificar backup
ls -lh src/ui/main_window.py*
```

**✅ Checklist Fase 1:**
- [ ] Branch correta confirmada
- [ ] Versão 1.1.0 confirmada
- [ ] Pasta `src/ui/styles/` criada
- [ ] Backup de `main_window.py` criado

---

## ✅ FASE 2: Copiar Arquivos Necessários

### 2.1 Copiar toast_notification.py
```bash
# Copiar arquivo de toast
cp old_code/mineru_desktop/ui/toast_notification.py src/ui/

# Verificar
wc -l src/ui/toast_notification.py
cat src/ui/toast_notification.py | head -30
```

### 2.2 Copiar stylesheets (themes)
```bash
# Copiar temas
cp old_code/mineru_desktop/ui/styles/dark_theme.qss src/ui/styles/
cp old_code/mineru_desktop/ui/styles/light_theme.qss src/ui/styles/

# Verificar
ls -lh src/ui/styles/
wc -l src/ui/styles/*.qss
```

### 2.3 Verificar imports do toast
```bash
# Verificar se toast usa imports corretos
grep -n "from mineru_desktop" src/ui/toast_notification.py
```

**❗ IMPORTANTE:** Se o grep acima encontrar imports de `mineru_desktop.*`, você NÃO precisa alterar nada, pois o arquivo está correto como está.

**✅ Checklist Fase 2:**
- [ ] `src/ui/toast_notification.py` copiado (170 linhas)
- [ ] `src/ui/styles/dark_theme.qss` copiado (264 linhas)
- [ ] `src/ui/styles/light_theme.qss` copiado (247 linhas)
- [ ] Imports verificados

---

## ✅ FASE 3: Integração no main_window.py

### 3.1 Adicionar imports no topo do arquivo

**Local:** `src/ui/main_window.py` (após linha 9)

```python
# Adicionar estes imports após "from pathlib import Path"
import sys
from datetime import datetime
```

**Local:** Após linha 16 (depois dos imports PySide6.QtCore)

```python
# Adicionar import de QTimer se não existir
from PySide6.QtCore import Qt, QUrl, QTimer
```

**Local:** Após linha 18 (depois de import de SettingsDialog)

```python
# Adicionar import do toast
from .toast_notification import ToastNotification, ToastType
```

### 3.2 Adicionar classe DragDropListWidget

**Local:** Inserir ANTES da classe `MainWindow` (linha 32)

```python
class DragDropListWidget(QListWidget):
    """List widget with drag and drop support for files."""

    def __init__(self, parent=None):
        """Initialize the drag-drop list widget."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.DragOnly)
        logger.debug("DragDropListWidget initialized")

    def dragEnterEvent(self, event):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            logger.debug("Drag enter accepted")
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        """Handle drag move events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        """Handle drop events."""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_paths = [url.toLocalFile() for url in urls if url.isLocalFile()]
            if file_paths:
                logger.info(f"Files dropped: {len(file_paths)}")
                # Emit signal to parent
                if hasattr(self.parent(), 'add_files_from_paths'):
                    self.parent().add_files_from_paths(file_paths)
            event.acceptProposedAction()
        else:
            event.ignore()
```

### 3.3 Adicionar atributo de tema no __init__

**Local:** `MainWindow.__init__()` (após linha 51, depois de `self.polling_worker`)

```python
        # Theme state
        self.current_theme = "light"
```

### 3.4 Aplicar tema no __init__

**Local:** `MainWindow.__init__()` (após `self.setup_ui()`, linha 54)

```python
        # Apply theme from config
        from ..config.config_manager import get_config
        config = get_config()
        saved_theme = config.get_theme_preference() if hasattr(config, 'get_theme_preference') else "light"
        self.apply_theme(saved_theme)
```

### 3.5 Adicionar menu "Visualizar" na _create_menu_bar()

**Local:** `_create_menu_bar()` (após linha 100, depois do menu File, ANTES do menu Help)

```python
        # View menu
        view_menu = menubar.addMenu("&Visualizar")

        # Theme toggle action
        self.theme_action = QAction("🌙 Tema Escuro", self)
        self.theme_action.triggered.connect(self.toggle_theme)
        view_menu.addAction(self.theme_action)
```

### 3.6 Substituir QListWidget por DragDropListWidget

**Local:** `_create_file_section()` (linha 130)

**DE:**
```python
        # File list
        self.file_list = QListWidget()
```

**PARA:**
```python
        # File list with drag & drop
        self.file_list = DragDropListWidget(self)
```

### 3.7 Adicionar método add_files_from_paths()

**Local:** Inserir APÓS o método `_add_files()` (após linha 221)

```python
    def add_files_from_paths(self, file_paths: list) -> None:
        """
        Add files from a list of paths (for drag & drop support).

        Args:
            file_paths: List of file paths to add
        """
        if not self.current_batch:
            self.current_batch = self.batch_service.create_batch([])

        added_count = 0
        for file_path in file_paths:
            # Avoid duplicates
            if not any(f.file_path == file_path for f in self.current_batch.files):
                file_info = self.current_batch.add_file(file_path)
                self._add_file_to_list(file_info.filename, file_path)
                added_count += 1

        # Enable process button if files are selected
        self.process_button.setEnabled(len(self.current_batch.files) > 0)

        if added_count > 0:
            ToastNotification.show_success(
                self,
                f"{added_count} arquivo(s) adicionado(s)",
                2000
            )
            logger.info(f"Added {added_count} files via drag & drop")
```

### 3.8 Substituir notificações por Toast

**Locations para substituir:**

#### 3.8.1 Em `_on_upload_completed()` (linha 315-321)
**SUBSTITUIR:**
```python
        if success_count > 0:
            QMessageBox.information(
                self,
                "Upload Concluído",
                f"Upload concluído!\n\nSucesso: {success_count}\nFalhas: {failed_count}\n\n"
                f"Batch ID: {batch.batch_id}\n\n"
                f"Verificando status automaticamente..."
            )
```

**POR:**
```python
        if success_count > 0:
            ToastNotification.show_success(
                self,
                f"Upload concluído! {success_count} sucesso, {failed_count} falhas",
                3000
            )
            # Keep the QMessageBox for batch ID info
            QMessageBox.information(
                self,
                "Upload Concluído",
                f"Batch ID: {batch.batch_id}\n\nVerificando status automaticamente..."
            )
```

#### 3.8.2 Em `_on_upload_completed()` - caso de falha (linha 326-330)
**ADICIONAR antes do QMessageBox:**
```python
        else:
            ToastNotification.show_error(
                self,
                f"Todos os uploads falharam ({failed_count} falhas)",
                4000
            )
            QMessageBox.critical(
                self,
                "Erro no Upload",
                f"Todos os uploads falharam.\n\nFalhas: {failed_count}"
            )
```

#### 3.8.3 Em `_on_upload_failed()` (após linha 343)
**ADICIONAR após o QMessageBox.critical:**
```python
        QMessageBox.critical(
            self,
            "Erro no Upload",
            f"Falha ao enviar arquivos:\n\n{error_message}"
        )

        ToastNotification.show_error(
            self,
            "Upload falhou!",
            3000
        )
```

#### 3.8.4 Em `_remove_selected_files()` (após linha 261)
**ADICIONAR após o logger.debug:**
```python
        logger.debug(f"Removed {len(selected_items)} files")

        ToastNotification.show_info(
            self,
            f"{len(selected_items)} arquivo(s) removido(s)",
            2000
        )
```

#### 3.8.5 Em `_on_all_complete()` (linha 401-406)
**ADICIONAR antes do QMessageBox:**
```python
        logger.info(f"Batch {batch.batch_id} completed: "
                   f"{summary['completed']} succeeded, {summary['failed']} failed")

        ToastNotification.show_success(
            self,
            f"Processamento concluído! {summary['completed']} sucesso, {summary['failed']} falhas",
            4000
        )

        QMessageBox.information(
            self,
            "Processamento Concluído",
            "Todos os arquivos foram processados!\n\n"
            "Clique em 'Abrir Pasta de Saída' para ver os resultados."
        )
```

### 3.9 Adicionar métodos de tema (toggle_theme e apply_theme)

**Local:** Inserir ANTES do método `_show_about()` (antes da linha 182)

```python
    def toggle_theme(self) -> None:
        """Toggle between light and dark theme."""
        new_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme(new_theme)

        # Save preference
        from ..config.config_manager import get_config
        config = get_config()
        if hasattr(config, 'save_theme_preference'):
            config.save_theme_preference(new_theme)

        logger.info(f"Theme changed to: {new_theme}")

    def apply_theme(self, theme: str) -> None:
        """
        Apply a theme to the application.

        Args:
            theme: Theme name ("light" or "dark")
        """
        self.current_theme = theme

        # Get stylesheet path
        if hasattr(sys, '_MEIPASS'):
            # Running as PyInstaller bundle
            base_path = Path(sys._MEIPASS)
        else:
            base_path = Path(__file__).parent

        stylesheet_path = base_path / "styles" / f"{theme}_theme.qss"

        # Load and apply stylesheet
        try:
            with open(stylesheet_path, "r") as f:
                stylesheet = f.read()
                self.setStyleSheet(stylesheet)

            # Update theme action text
            if hasattr(self, 'theme_action'):
                if theme == "light":
                    self.theme_action.setText("🌙 Tema Escuro")
                else:
                    self.theme_action.setText("☀️ Tema Claro")

            logger.info(f"Applied {theme} theme")

        except Exception as e:
            logger.error(f"Failed to load theme '{theme}': {e}")
            # Fallback to default
            self.setStyleSheet("")
```

### 3.10 Adicionar emojis nos botões

**Local:** Método `_create_file_section()` (linha 122)

**SUBSTITUIR:**
```python
        self.add_files_button = QPushButton("Adicionar Arquivos...")
```

**POR:**
```python
        self.add_files_button = QPushButton("📁 Adicionar Arquivos...")
```

**Local:** Método `_create_file_section()` (linha 135)

**SUBSTITUIR:**
```python
        remove_button = QPushButton("Remover Selecionados")
```

**POR:**
```python
        remove_button = QPushButton("🗑️ Remover Selecionados")
        remove_button.setObjectName("dangerButton")
```

**Local:** Método `_create_processing_section()` (linha 156)

**SUBSTITUIR:**
```python
        self.process_button = QPushButton("Iniciar Processamento")
```

**POR:**
```python
        self.process_button = QPushButton("▶️ Iniciar Processamento")
```

**Local:** Método `_create_processing_section()` (linha 162)

**SUBSTITUIR:**
```python
        self.open_folder_button = QPushButton("Abrir Pasta de Saída")
```

**POR:**
```python
        self.open_folder_button = QPushButton("📂 Abrir Pasta de Saída")
        self.open_folder_button.setObjectName("secondaryButton")
```

**✅ Checklist Fase 3:**
- [ ] Imports adicionados (sys, datetime, QTimer, ToastNotification)
- [ ] Classe `DragDropListWidget` adicionada
- [ ] Atributo `self.current_theme` adicionado
- [ ] Tema aplicado no `__init__()`
- [ ] Menu "Visualizar" adicionado
- [ ] `QListWidget` substituído por `DragDropListWidget`
- [ ] Método `add_files_from_paths()` adicionado
- [ ] Toast notifications integrados (5 locais)
- [ ] Métodos `toggle_theme()` e `apply_theme()` adicionados
- [ ] Emojis adicionados aos botões (4 botões)

---

## ✅ FASE 4: Adicionar Métodos de Tema ao ConfigManager

### 4.1 Ler ConfigManager atual
```bash
cat src/config/config_manager.py | tail -50
```

### 4.2 Adicionar métodos de tema

**Local:** Inserir NO FINAL da classe `ConfigManager` (antes do último método ou no final do arquivo)

```python
    def get_theme_preference(self) -> str:
        """
        Get theme preference from config.

        Returns:
            Theme name ("light" or "dark")
        """
        config_file = CONFIG_FILE

        if not os.path.exists(config_file):
            return "light"

        try:
            config = configparser.ConfigParser()
            config.read(config_file)

            if "UI" in config:
                theme = config["UI"].get("theme", "light")
                logger.debug(f"Loaded theme preference: {theme}")
                return theme
        except Exception as e:
            logger.error(f"Error loading theme preference: {e}")

        return "light"

    def save_theme_preference(self, theme: str) -> None:
        """
        Save theme preference to config.

        Args:
            theme: Theme name ("light" or "dark")
        """
        config_file = CONFIG_FILE

        try:
            config = configparser.ConfigParser()

            if os.path.exists(config_file):
                config.read(config_file)

            if "UI" not in config:
                config["UI"] = {}

            config["UI"]["theme"] = theme

            with open(config_file, "w") as configfile:
                config.write(configfile)

            logger.info(f"Theme preference saved: {theme}")

        except Exception as e:
            logger.error(f"Failed to save theme preference: {e}")
```

### 4.3 Verificar imports no ConfigManager

**Verificar se estes imports existem no topo do arquivo:**

```bash
grep "import configparser" src/config/config_manager.py
grep "import os" src/config/config_manager.py
```

Se não existirem, adicionar no topo:

```python
import configparser
import os
```

**✅ Checklist Fase 4:**
- [ ] Métodos `get_theme_preference()` e `save_theme_preference()` adicionados
- [ ] Imports verificados (`configparser`, `os`)
- [ ] Código compila sem erros

---

## ✅ FASE 5: Atualizar MinerU.spec para Incluir Stylesheets

### 5.1 Ler MinerU.spec atual
```bash
cat MinerU.spec | grep -A 20 "datas="
```

### 5.2 Adicionar stylesheets aos datas

**Local:** Seção `datas=` do arquivo `MinerU.spec`

**Adicionar:**
```python
datas=[
    ('src/ui/styles/*.qss', 'src/ui/styles'),
    # ... outros datas existentes
],
```

**Exemplo completo:**
```python
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('src/ui/styles/*.qss', 'src/ui/styles'),
        ('mineru_icon.svg', '.'),
        ('version.py', '.'),
    ],
    # ... resto da configuração
)
```

**✅ Checklist Fase 5:**
- [ ] `MinerU.spec` atualizado com stylesheets
- [ ] Sintaxe verificada

---

## ✅ FASE 6: Validação e Testes

### 6.1 Verificar sintaxe Python
```bash
python3 -m py_compile src/ui/main_window.py
python3 -m py_compile src/ui/toast_notification.py
python3 -m py_compile src/config/config_manager.py

echo "✅ Sintaxe verificada!"
```

### 6.2 Contar linhas do novo main_window.py
```bash
wc -l src/ui/main_window.py
# Esperado: ~600-650 linhas (similar ao código antigo)
```

### 6.3 Verificar imports
```bash
# Verificar se todos os imports estão corretos
python3 -c "from src.ui.main_window import MainWindow; print('✅ Imports OK')"
python3 -c "from src.ui.toast_notification import ToastNotification; print('✅ Toast imports OK')"
```

### 6.4 Testes manuais (recomendado)

**Se possível, executar a aplicação:**

```bash
# Executar aplicação
python3 main.py
```

**Checklist de testes manuais:**
- [ ] Aplicação abre sem erros
- [ ] Tema light aplicado por padrão
- [ ] Menu "Visualizar" → "🌙 Tema Escuro" existe
- [ ] Toggle de tema funciona (light ↔ dark)
- [ ] Tema persiste após fechar e reabrir
- [ ] Drag & drop de arquivos funciona
- [ ] Toast notification aparece ao adicionar arquivos
- [ ] Toast notification aparece ao remover arquivos
- [ ] Upload mostra toast de sucesso/erro
- [ ] Botões têm emojis corretos
- [ ] Stylesheets aplicados (cores diferentes nos temas)
- [ ] Sem erros no console

**✅ Checklist Fase 6:**
- [ ] Sintaxe Python validada (3 arquivos)
- [ ] Linhas do main_window.py: ~600-650
- [ ] Imports validados
- [ ] Testes manuais realizados (se possível)

---

## ✅ FASE 7: Atualizar Versão para 1.2.0 e CHANGELOG

### 7.1 Atualizar version.py
```bash
cat > version.py << 'EOF'
# Version file for MinerU Desktop Client
VERSION = "1.2.0"
EOF

cat version.py
```

### 7.2 Atualizar CHANGELOG.md

**Adicionar no topo do arquivo (após linha 7):**

```markdown
## [1.2.0] - 2025-11-21

### ✨ Features Modernas de UI Restauradas

Após o refactoring da v1.1.0, restauramos as features de UI moderna que estavam no código antigo:

#### Adicionado
- **Toast Notifications**: Notificações não-intrusivas com animações de fade
  - Tipos: INFO, SUCCESS, ERROR, WARNING
  - Classe `ToastNotification` com métodos estáticos
  - Integração em 5 pontos da aplicação
- **Drag & Drop**: Suporte completo para arrastar arquivos para a janela
  - Classe `DragDropListWidget` com eventos de drag/drop
  - Validação de URLs e arquivos locais
  - Feedback visual durante arrasto
- **Theme Switcher**: Alternância entre tema claro e escuro
  - Menu "Visualizar" com action de toggle
  - Métodos `toggle_theme()` e `apply_theme()`
  - Persistência de preferência no `config.ini` (seção `[UI]`)
  - Stylesheets completos: `dark_theme.qss` (264 linhas) e `light_theme.qss` (247 linhas)
- **Emojis nos Botões**: UX moderna com ícones visuais
  - 📁 Adicionar Arquivos
  - 🗑️ Remover Selecionados
  - ▶️ Iniciar Processamento
  - 📂 Abrir Pasta de Saída
- **ConfigManager Theme Methods**:
  - `get_theme_preference()` - Carrega tema salvo
  - `save_theme_preference(theme)` - Persiste escolha do usuário

#### Arquivos Novos
- `src/ui/toast_notification.py` (170 linhas)
- `src/ui/styles/dark_theme.qss` (264 linhas)
- `src/ui/styles/light_theme.qss` (247 linhas)

#### Modificado
- `src/ui/main_window.py`: 468 → ~620 linhas
  - Classe `DragDropListWidget` adicionada
  - Integração de toast notifications
  - Theme switcher implementado
  - Método `add_files_from_paths()` para drag & drop
- `src/config/config_manager.py`: Métodos de tema adicionados
- `MinerU.spec`: Stylesheets incluídos no bundle

#### UX Melhorada
- Feedback visual imediato com toasts (sem bloquear a UI)
- Tema escuro para reduzir fadiga ocular
- Drag & drop para workflow mais rápido
- Interface mais polida e moderna

### Compatibilidade
- ✅ 100% compatível com configurações v1.1.0
- ✅ Migração automática (tema padrão: light)
- ✅ Todas as funcionalidades v1.1.0 mantidas

### Estatísticas
- **Linhas adicionadas**: ~680 linhas de UI moderna
- **Arquivos novos**: 3 (toast + 2 themes)
- **Breaking changes**: Nenhum

```

### 7.3 Atualizar link de versão no final do CHANGELOG

**Adicionar na seção de links (linha ~100):**

```markdown
[1.2.0]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.2.0
```

**✅ Checklist Fase 7:**
- [ ] `version.py` atualizado para 1.2.0
- [ ] CHANGELOG.md atualizado com seção 1.2.0
- [ ] Link de versão adicionado no final

---

## ✅ FASE 8: Commit, Push e Build

### 8.1 Verificar arquivos modificados
```bash
git status
```

**Arquivos esperados:**
```
Modified:
  - src/ui/main_window.py
  - src/config/config_manager.py
  - MinerU.spec
  - version.py
  - CHANGELOG.md

New files:
  - src/ui/toast_notification.py
  - src/ui/styles/dark_theme.qss
  - src/ui/styles/light_theme.qss
  - MIGRATION_UI_FEATURES.md (este documento)
```

### 8.2 Adicionar arquivos ao staging
```bash
git add src/ui/main_window.py
git add src/ui/toast_notification.py
git add src/ui/styles/dark_theme.qss
git add src/ui/styles/light_theme.qss
git add src/config/config_manager.py
git add MinerU.spec
git add version.py
git add CHANGELOG.md
git add MIGRATION_UI_FEATURES.md
```

### 8.3 Verificar diff
```bash
git diff --cached --stat
```

### 8.4 Commit
```bash
git commit -m "$(cat <<'EOF'
feat: Restore modern UI features (v1.2.0)

Restore UI features lost during v1.1.0 refactoring:

✨ Features Added:
- Toast notifications (non-intrusive feedback)
- Drag & drop file support
- Theme switcher (dark/light mode)
- Modern button emojis
- Theme persistence in config

📁 Files Added:
- src/ui/toast_notification.py (170 lines)
- src/ui/styles/dark_theme.qss (264 lines)
- src/ui/styles/light_theme.qss (247 lines)

🔄 Files Modified:
- src/ui/main_window.py: 468 → ~620 lines
  * Added DragDropListWidget class
  * Integrated toast notifications
  * Added toggle_theme() and apply_theme()
  * Added add_files_from_paths() method
- src/config/config_manager.py:
  * Added get_theme_preference()
  * Added save_theme_preference()
- MinerU.spec: Include stylesheets in bundle
- version.py: Bump to 1.2.0
- CHANGELOG.md: Document v1.2.0 changes

📊 Stats:
- ~680 lines of modern UI code added
- 3 new files (toast + 2 themes)
- 100% backward compatible with v1.1.0

Migration guide: MIGRATION_UI_FEATURES.md
EOF
)"
```

### 8.5 Push
```bash
git push -u origin claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
```

### 8.6 Verificar push
```bash
git log --oneline -1
git status
```

### 8.7 Build AppImage (Opcional - apenas se tiver ambiente configurado)

```bash
# Apenas se quiser gerar novo AppImage
./build_appimage.sh

# Verificar versão do AppImage gerado
ls -lh MinerU-*.AppImage
./MinerU-1.2.0-x86_64.AppImage --version 2>&1 | head -5
```

**✅ Checklist Fase 8:**
- [ ] Git status verificado (9 arquivos)
- [ ] Arquivos adicionados ao staging
- [ ] Diff revisado
- [ ] Commit realizado com mensagem detalhada
- [ ] Push realizado com sucesso
- [ ] Log verificado
- [ ] (Opcional) AppImage v1.2.0 gerado

---

## 🎯 CHECKLIST FINAL

### Código
- [ ] `src/ui/toast_notification.py` existe e compila
- [ ] `src/ui/styles/dark_theme.qss` existe (264 linhas)
- [ ] `src/ui/styles/light_theme.qss` existe (247 linhas)
- [ ] `src/ui/main_window.py` tem ~620 linhas
- [ ] Classe `DragDropListWidget` implementada
- [ ] Métodos `toggle_theme()` e `apply_theme()` implementados
- [ ] Método `add_files_from_paths()` implementado
- [ ] Toast integrado em 5 locais
- [ ] ConfigManager tem métodos de tema
- [ ] MinerU.spec inclui stylesheets

### Versão e Documentação
- [ ] `version.py` = "1.2.0"
- [ ] CHANGELOG.md tem seção [1.2.0]
- [ ] CHANGELOG.md tem link de versão
- [ ] MIGRATION_UI_FEATURES.md commitado

### Git
- [ ] Branch: `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE`
- [ ] Commit com mensagem detalhada
- [ ] Push realizado com sucesso
- [ ] 9 arquivos commitados

### Funcional (se testado)
- [ ] Aplicação abre sem erros
- [ ] Drag & drop funciona
- [ ] Toast notifications aparecem
- [ ] Theme switcher funciona (light ↔ dark)
- [ ] Tema persiste após reabrir
- [ ] Emojis visíveis nos botões
- [ ] Sem erros no console

---

## 📚 REFERÊNCIAS

### Arquivos de Origem
- **Toast**: `old_code/mineru_desktop/ui/toast_notification.py`
- **Main Window Antigo**: `old_code/mineru_desktop/ui/main_window.py` (625 linhas)
- **Config Antigo**: `old_code/mineru_desktop/core/config.py`
- **Themes**: `old_code/mineru_desktop/ui/styles/*.qss`

### Commits Relevantes
- **v1.1.0 Refactoring**: e6bcb83 - "chore: Bump version to 1.1.0 after major refactoring"
- **Consolidation**: d62bbc0 - "refactor: Consolidate codebase to single src/ implementation"

### Comparação de Código
| Feature | Old Code (625L) | New Code (468L) | v1.2.0 Target (~620L) |
|---------|----------------|-----------------|----------------------|
| Toast Notifications | ✅ | ❌ | ✅ |
| Drag & Drop | ✅ | ❌ | ✅ |
| Theme Switcher | ✅ | ❌ | ✅ |
| Emojis | ✅ | ⚠️ | ✅ |
| ConfigManager Themes | ✅ | ❌ | ✅ |

---

## 🎨 LOGOS DISPONÍVEIS

Para uso futuro em branding ou documentação:

- **Logo 1**: https://mineru.net/logo.png
- **Logo 2**: https://gcore.jsdelivr.net/gh/opendatalab/MinerU@master/docs/images/MinerU-logo.png

---

## 🚀 PRÓXIMOS PASSOS (APÓS MIGRAÇÃO)

### 1. Testar Completamente
```bash
# Executar aplicação
python3 main.py

# Testar todos os fluxos:
# - Adicionar arquivos (dialog + drag & drop)
# - Remover arquivos
# - Alternar tema (light/dark)
# - Upload de arquivos
# - Ver toasts em cada ação
# - Verificar persistência de tema
```

### 2. Build e Release
```bash
# Build AppImage
./build_appimage.sh

# Criar release tag
git tag -a v1.2.0 -m "Release v1.2.0: Modern UI Features"
git push origin v1.2.0

# Usar release.sh para publicar
./release.sh
```

### 3. Merge para Main
```bash
# Após validação completa
git checkout main
git merge claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
git push origin main
```

---

## ⚠️ PROBLEMAS CONHECIDOS E SOLUÇÕES

### Problema: Theme não carrega ao iniciar
**Solução:**
- Verificar se `config.ini` existe e tem seção `[UI]`
- Verificar permissões do arquivo
- Verificar logs: `grep theme ~/.config/mineru/logs/*.log`

### Problema: Stylesheets não encontrados
**Solução:**
```bash
# Verificar estrutura de pastas
ls -la src/ui/styles/

# Verificar se MinerU.spec inclui stylesheets
grep "styles" MinerU.spec

# Rebuild AppImage
./build_appimage.sh
```

### Problema: Drag & drop não funciona
**Solução:**
- Verificar se `DragDropListWidget` está sendo usado (não `QListWidget`)
- Verificar método `add_files_from_paths()` existe
- Verificar logs de drag events

### Problema: Toast não aparece
**Solução:**
- Verificar import: `from .toast_notification import ToastNotification`
- Verificar se parent window está sendo passado corretamente
- Verificar se toast está sendo instanciado dentro de um QTimer (pode precisar de `QApplication.processEvents()`)

---

## 📋 RESUMO EXECUTIVO

| Aspecto | Detalhes |
|---------|----------|
| **Objetivo** | Restaurar features de UI moderna perdidas no refactoring v1.1.0 |
| **Versão Atual** | 1.1.0 |
| **Versão Alvo** | 1.2.0 |
| **Tempo Estimado** | 60-75 minutos |
| **Complexidade** | Média (requer atenção aos detalhes) |
| **Breaking Changes** | Nenhum |
| **Features Restauradas** | 5 (Toast, Drag&Drop, Themes, Emojis, ConfigManager) |
| **Arquivos Novos** | 3 |
| **Arquivos Modificados** | 5 |
| **Linhas Adicionadas** | ~680 |
| **Testes Requeridos** | 12 testes manuais de UI |
| **Branch** | `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE` |

---

## 💡 DICAS PARA EXECUÇÃO

1. **Siga as fases na ordem**: Não pule fases para evitar erros de dependência
2. **Valide cada fase**: Use os checklists para garantir completude
3. **Faça commits incrementais**: Se preferir, pode commitar após cada fase (2, 3, 4, 5)
4. **Teste localmente**: Se possível, rode `python3 main.py` após Fase 6
5. **Backup automático**: Fase 1 cria backup de `main_window.py`
6. **Use diff**: Sempre revise `git diff` antes de commitar
7. **Logs são seus amigos**: Em caso de erro, verifique logs da aplicação

---

## 📞 SUPORTE

Se encontrar problemas durante a migração:

1. **Verificar logs**: `~/.config/mineru/logs/`
2. **Revisar este documento**: Seção "Problemas Conhecidos"
3. **Comparar com código antigo**: `old_code/mineru_desktop/ui/main_window.py`
4. **Reverter se necessário**: `git checkout src/ui/main_window.py.backup`

---

**Documento criado em:** 2025-11-21
**Versão do documento:** 1.0
**Para uso em:** MinerU Desktop Client v1.1.0 → v1.2.0
**Branch:** `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE`

---

🎉 **Boa sorte com a migração!** Este documento foi criado para ser seguido passo a passo por um agente AI ou desenvolvedor, com todos os comandos e código prontos para copiar e colar.
