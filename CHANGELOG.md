# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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
  - Stylesheets completos: `dark_theme.qss` (263 linhas) e `light_theme.qss` (246 linhas)
- **Emojis nos Botões**: UX moderna com ícones visuais
  - 📁 Adicionar Arquivos
  - 🗑️ Remover Selecionados
  - ▶️ Iniciar Processamento
  - 📂 Abrir Pasta de Saída
- **ConfigManager Theme Methods**:
  - `get_theme_preference()` - Carrega tema salvo
  - `save_theme_preference(theme)` - Persiste escolha do usuário

#### Arquivos Novos
- `src/ui/toast_notification.py` (169 linhas)
- `src/ui/styles/dark_theme.qss` (263 linhas)
- `src/ui/styles/light_theme.qss` (246 linhas)

#### Modificado
- `src/ui/main_window.py`: 468 → 635 linhas
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

## [1.1.0] - 2025-11-21

### Refatoração Major
- **Consolidação completa da base de código**: Eliminadas 3 implementações duplicadas
- Removidas ~4.000 linhas de código duplicado (redução de 90%)
- Estrutura unificada em `src/` com arquitetura modular
- Código antigo movido para `old_code/` (backup)

### Mudanças Técnicas
- Entry point único: `main.py` (importa de `src/`)
- Build configuration (`MinerU.spec`) atualizado para módulos `src/`
- Logging já implementado corretamente (sem print statements)
- Configuração centralizada em `src/config/constants.py`
- Documentação atualizada para refletir arquitetura atual

### Arquivos Consolidados
- `mineru_client.py` (679 linhas) → `src/services/api_client.py`
- `settings_dialog.py` (341 linhas) → `src/ui/settings_dialog.py`
- `validators.py` (254 linhas) → validação em `src/`
- `exceptions.py` (123 linhas) → exceções em `src/services/`
- Diretório `mineru_desktop/` removido (implementação alternativa)
- `run.py` removido (obsoleto)

### Arquitetura Final
```
src/
├── config/        # Configuração centralizada
├── services/      # API client e batch service
├── ui/            # Interface Qt (MainWindow, SettingsDialog)
├── workers/       # Upload e polling workers
├── models/        # Modelos de dados
└── utils/         # Logging e utilitários
```

### Compatibilidade
- ✅ Funcionalidades mantidas 100%
- ✅ Interface de usuário inalterada
- ✅ Configurações existentes compatíveis
- ✅ AppImage build compatível

## [1.0.1] - 2025-11-18

### Correções
- Melhorias na verificação de status de processamento em lote
- Maior confiabilidade no processamento de múltiplos arquivos
- Correções de bugs no sistema de upload e download

### Mudanças
- AppImage atualizado para versão 1.0.1
- README mantém informações atualizadas sobre o sistema

## [1.0.0] - 2025-11-18

### Adicionado
- Sistema de versionamento automático com `version.py`
- Script de release automatizado (`release.sh`)
- Documentação completa do processo de release (`RELEASE_PROCESS.md`)
- CHANGELOG para rastreamento de mudanças
- AppImage versionado com symlink para última versão
- Seleção de modelo VLM (Pipeline ou VLM)
- Suporte otimizado para português com modelo Pipeline
- Extração automática de arquivos ZIP após download

### Funcionalidades Principais
- Configuração segura de Token da API (via Linux Keyring)
- Upload de arquivos em lote com validação de tipo
- Upload paralelo para melhor desempenho (até 5 arquivos simultâneos)
- Barra de progresso durante uploads
- Polling automático de status de processamento (a cada 10 segundos)
- Download automático de resultados para pasta definida pelo usuário
- Botão para abrir a pasta de saída no gerenciador de arquivos
- Feedback de progresso em tempo real
- Tratamento robusto de erros
- Interface em Português

### Tipos de Arquivo Suportados
- Documentos: PDF, DOCX, PPTX
- Imagens: JPG, PNG

### Documentação
- README.md completo em português
- Guia de build (BUILD.md)
- Documentação de dependências do sistema (SYSTEM_DEPENDENCIES.md)
- Workflow de desenvolvimento (WORKFLOW.md)

## Formato de Versões

- **MAJOR**: Mudanças incompatíveis na API
- **MINOR**: Novas funcionalidades de forma compatível
- **PATCH**: Correções de bugs compatíveis

[1.2.0]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.2.0
[1.1.0]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.1.0
[1.0.1]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.0.1
[1.0.0]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.0.0
