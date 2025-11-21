# 🚀 INSTRUÇÕES PARA EXECUTAR MIGRAÇÃO DE UI - v1.2.0

**⏱️ Tempo estimado:** 60-75 minutos
**📋 Documento de referência:** `MIGRATION_UI_FEATURES.md`
**🎯 Objetivo:** Restaurar features de UI moderna perdidas no refactoring v1.1.0

---

## 📌 CONTEXTO RÁPIDO

Durante o refactoring v1.1.0, perdemos **5 features modernas de UI**:
1. 🔔 **Toast Notifications** (notificações não-intrusivas)
2. 🖱️ **Drag & Drop** de arquivos
3. 🎨 **Theme Switcher** (dark/light mode)
4. 💫 **Emojis nos botões** (UX moderna)
5. ⚙️ **ConfigManager theme methods**

**Evidência:**
- `old_code/mineru_desktop/ui/main_window.py`: **625 linhas** ✅ (COM features)
- `src/ui/main_window.py`: **468 linhas** ❌ (SEM features)
- **Diferença:** ~157 linhas de UI moderna perdidas

---

## ✅ PRÉ-REQUISITOS

Antes de começar, confirme:

```bash
# 1. Verificar branch correta
git branch --show-current
# Esperado: claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE

# 2. Verificar versão atual
cat version.py
# Esperado: VERSION = "1.1.0"

# 3. Verificar que código antigo existe
ls old_code/mineru_desktop/ui/main_window.py
ls old_code/mineru_desktop/ui/toast_notification.py
ls old_code/mineru_desktop/ui/styles/*.qss
# Todos devem existir

# 4. Verificar documento de migração
cat MIGRATION_UI_FEATURES.md | head -20
# Deve mostrar o documento completo com 1107 linhas
```

✅ **Se todos os comandos acima funcionaram, você está pronto para iniciar!**

---

## 🎯 EXECUÇÃO - SIGA ESTAS ETAPAS NA ORDEM

### IMPORTANTE:
- ✅ **LEIA** o arquivo `MIGRATION_UI_FEATURES.md` ANTES de começar
- ✅ **SIGA** as 8 fases na ordem exata
- ✅ **VALIDE** cada fase com os checklists fornecidos
- ✅ **NÃO PULE** nenhuma etapa

---

## 📖 FASE 1: PREPARAÇÃO (10 minutos)

**Ações:**
1. Ler a seção completa "FASE 1" do `MIGRATION_UI_FEATURES.md`
2. Executar todos os comandos bash de verificação
3. Criar pasta `src/ui/styles/`
4. Fazer backup de `src/ui/main_window.py`

**Validação:**
```bash
# Checklist Fase 1
ls src/ui/styles/                    # Pasta existe
ls src/ui/main_window.py.backup      # Backup existe
git status                           # Working tree clean
```

---

## 📖 FASE 2: COPIAR ARQUIVOS (5 minutos)

**Ações:**
1. Copiar `toast_notification.py` para `src/ui/`
2. Copiar `dark_theme.qss` e `light_theme.qss` para `src/ui/styles/`
3. Verificar que os arquivos foram copiados corretamente

**Comandos principais:**
```bash
cp old_code/mineru_desktop/ui/toast_notification.py src/ui/
cp old_code/mineru_desktop/ui/styles/dark_theme.qss src/ui/styles/
cp old_code/mineru_desktop/ui/styles/light_theme.qss src/ui/styles/
```

**Validação:**
```bash
# Checklist Fase 2
wc -l src/ui/toast_notification.py       # 170 linhas
wc -l src/ui/styles/dark_theme.qss       # 264 linhas
wc -l src/ui/styles/light_theme.qss      # 247 linhas
```

---

## 📖 FASE 3: INTEGRAÇÃO NO MAIN_WINDOW.PY (30 minutos)

**⚠️ ESTA É A FASE MAIS IMPORTANTE E COMPLEXA!**

**Ações:**
1. Adicionar imports (5 locais diferentes)
2. Adicionar classe `DragDropListWidget` (antes da classe MainWindow)
3. Modificar `MainWindow.__init__()` (2 alterações)
4. Adicionar menu "Visualizar" na `_create_menu_bar()`
5. Substituir `QListWidget` por `DragDropListWidget` em `_create_file_section()`
6. Adicionar método `add_files_from_paths()` (novo método completo)
7. Adicionar toasts em 5 locais diferentes
8. Adicionar métodos `toggle_theme()` e `apply_theme()`
9. Adicionar emojis nos 4 botões

**📋 Use a seção "FASE 3" do `MIGRATION_UI_FEATURES.md`** - tem TODO o código pronto para copiar!

**Dica:** Faça uma alteração por vez e valide com:
```bash
python3 -m py_compile src/ui/main_window.py
```

**Validação:**
```bash
# Checklist Fase 3 (resumido)
grep -c "DragDropListWidget" src/ui/main_window.py    # Deve ser > 2
grep -c "ToastNotification" src/ui/main_window.py     # Deve ser > 5
grep -c "toggle_theme" src/ui/main_window.py          # Deve ser > 1
grep -c "apply_theme" src/ui/main_window.py           # Deve ser > 1
grep -c "📁\|🗑️\|▶️\|📂" src/ui/main_window.py        # Deve ser 4 (emojis)
wc -l src/ui/main_window.py                           # ~600-650 linhas
```

---

## 📖 FASE 4: CONFIGMANAGER THEME METHODS (10 minutos)

**Ações:**
1. Abrir `src/config/config_manager.py`
2. Adicionar métodos `get_theme_preference()` e `save_theme_preference()` no final da classe
3. Verificar imports (`configparser`, `os`)

**📋 Use a seção "FASE 4" do `MIGRATION_UI_FEATURES.md`** - tem o código completo!

**Validação:**
```bash
grep -c "get_theme_preference" src/config/config_manager.py    # Deve ser > 1
grep -c "save_theme_preference" src/config/config_manager.py   # Deve ser > 1
python3 -m py_compile src/config/config_manager.py             # Sem erros
```

---

## 📖 FASE 5: ATUALIZAR MINERU.SPEC (5 minutos)

**Ações:**
1. Adicionar stylesheets aos `datas=` do `MinerU.spec`

**Código a adicionar:**
```python
datas=[
    ('src/ui/styles/*.qss', 'src/ui/styles'),
    # ... outros datas existentes
],
```

**Validação:**
```bash
grep "styles/\*\.qss" MinerU.spec    # Deve encontrar a linha
```

---

## 📖 FASE 6: VALIDAÇÃO E TESTES (5 minutos)

**Ações:**
1. Compilar todos os arquivos Python modificados
2. Contar linhas do novo main_window.py
3. **(OPCIONAL)** Executar aplicação e testar manualmente

**Comandos:**
```bash
python3 -m py_compile src/ui/main_window.py
python3 -m py_compile src/ui/toast_notification.py
python3 -m py_compile src/config/config_manager.py

wc -l src/ui/main_window.py    # Esperado: ~600-650 linhas
```

**Teste manual (se possível):**
```bash
python3 main.py
# Teste: drag & drop, toggle tema, adicionar/remover arquivos
```

---

## 📖 FASE 7: ATUALIZAR VERSÃO E CHANGELOG (10 minutos)

**Ações:**
1. Atualizar `version.py` para `1.2.0`
2. Adicionar seção `[1.2.0]` no `CHANGELOG.md`
3. Adicionar link de versão no final do CHANGELOG

**📋 Use a seção "FASE 7" do `MIGRATION_UI_FEATURES.md`** - tem o texto completo do CHANGELOG!

**Comandos principais:**
```bash
cat > version.py << 'EOF'
# Version file for MinerU Desktop Client
VERSION = "1.2.0"
EOF

# Editar CHANGELOG.md (use o conteúdo fornecido na FASE 7)
```

**Validação:**
```bash
cat version.py                            # VERSION = "1.2.0"
grep "## \[1.2.0\]" CHANGELOG.md         # Encontra seção
grep "\[1.2.0\]:" CHANGELOG.md | tail -1  # Link existe
```

---

## 📖 FASE 8: COMMIT E PUSH (5 minutos)

**Ações:**
1. Adicionar todos os arquivos ao staging
2. Fazer commit com mensagem detalhada
3. Push para a branch

**📋 Use a seção "FASE 8" do `MIGRATION_UI_FEATURES.md`** - tem o commit message completo!

**Comandos principais:**
```bash
git add src/ui/main_window.py
git add src/ui/toast_notification.py
git add src/ui/styles/dark_theme.qss
git add src/ui/styles/light_theme.qss
git add src/config/config_manager.py
git add MinerU.spec
git add version.py
git add CHANGELOG.md

# Commit (use a mensagem da FASE 8)
git commit -m "feat: Restore modern UI features (v1.2.0) ..."

# Push
git push -u origin claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
```

**Validação:**
```bash
git log --oneline -1              # Commit existe
git status                        # Working tree clean
git push -n origin HEAD           # Dry run (se quiser verificar antes)
```

---

## ✅ CHECKLIST FINAL

Antes de considerar completo, verifique:

### Arquivos
- [ ] `src/ui/toast_notification.py` existe (170 linhas)
- [ ] `src/ui/styles/dark_theme.qss` existe (264 linhas)
- [ ] `src/ui/styles/light_theme.qss` existe (247 linhas)
- [ ] `src/ui/main_window.py` tem ~600-650 linhas
- [ ] `src/config/config_manager.py` modificado
- [ ] `MinerU.spec` inclui stylesheets

### Versão
- [ ] `version.py` = "1.2.0"
- [ ] `CHANGELOG.md` tem seção [1.2.0]
- [ ] Link de versão adicionado no CHANGELOG

### Git
- [ ] 9 arquivos commitados (7 modificados + 3 novos)
- [ ] Commit tem mensagem detalhada
- [ ] Push realizado com sucesso
- [ ] Branch: `claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE`

### Código (validação rápida)
- [ ] `python3 -m py_compile src/ui/main_window.py` → sem erros
- [ ] `python3 -m py_compile src/ui/toast_notification.py` → sem erros
- [ ] `python3 -m py_compile src/config/config_manager.py` → sem erros
- [ ] `grep -c "DragDropListWidget" src/ui/main_window.py` → > 2
- [ ] `grep -c "ToastNotification" src/ui/main_window.py` → > 5

---

## 🎯 PROMPT PARA VOCÊ (PRÓXIMO CHAT)

Copie e use este prompt quando iniciar:

```
Olá! Vou executar a migração de features de UI moderna para o
MinerU Desktop Client, versão 1.1.0 → 1.2.0.

Por favor, siga estas instruções NA ORDEM:

1. Leia o arquivo EXECUTE_MIGRATION.md (este arquivo)
2. Verifique os pré-requisitos (comandos fornecidos)
3. Leia o arquivo MIGRATION_UI_FEATURES.md (1107 linhas - guia completo)
4. Execute as 8 FASES sequencialmente conforme documentado
5. Valide CADA fase com os checklists fornecidos
6. Ao final, verifique o CHECKLIST FINAL (14 itens)

IMPORTANTE:
- NÃO pule fases
- NÃO improvise código - use o fornecido no MIGRATION_UI_FEATURES.md
- VALIDE cada etapa antes de prosseguir
- Use os comandos bash exatos fornecidos

Objetivo: Restaurar 5 features de UI (toast, drag&drop, themes,
emojis, config) perdidas no refactoring v1.1.0.

Branch: claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE

Estou pronto para começar!
```

---

## 📚 DOCUMENTAÇÃO DE APOIO

### Arquivos Principais
- **`MIGRATION_UI_FEATURES.md`** (1107 linhas) - Guia técnico completo com TODO o código
- **`EXECUTE_MIGRATION.md`** (este arquivo) - Instruções executivas resumidas

### Arquivos de Origem
- `old_code/mineru_desktop/ui/main_window.py` (625 linhas)
- `old_code/mineru_desktop/ui/toast_notification.py` (170 linhas)
- `old_code/mineru_desktop/ui/styles/*.qss` (511 linhas total)

### Arquivos de Destino
- `src/ui/main_window.py` (468 → ~620 linhas)
- `src/ui/toast_notification.py` (novo, 170 linhas)
- `src/ui/styles/*.qss` (novos, 511 linhas)
- `src/config/config_manager.py` (+50 linhas)

---

## ⚠️ PROBLEMAS COMUNS

### Erro: "Module not found"
**Solução:** Verifique imports no topo dos arquivos

### Erro: "Syntax error" no Python
**Solução:** Revise o código copiado - pode ter indentação errada

### Conflito ao fazer push
**Solução:**
```bash
git fetch origin
git rebase origin/claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
git push -u origin claude/refactor-mineru-desktop-01CkTGLS1t3Ugyao2cYzSxUE
```

### Stylesheets não carregam
**Solução:** Verifique `MinerU.spec` - deve incluir `('src/ui/styles/*.qss', 'src/ui/styles')`

---

## 🎉 RESULTADO ESPERADO

Após completar todas as fases:

```
✅ Versão 1.2.0
✅ Toast notifications funcionando
✅ Theme switcher (dark/light mode)
✅ Drag & drop de arquivos
✅ Emojis nos botões
✅ ConfigManager com theme methods
✅ ~680 linhas de código UI moderno adicionadas
✅ 100% compatível com v1.1.0
✅ 0 breaking changes
✅ Pronto para merge na main
```

---

## 📞 EM CASO DE DÚVIDAS

1. **Consulte primeiro:** `MIGRATION_UI_FEATURES.md` - seção de troubleshooting
2. **Verifique:** Logs de erro em `~/.config/mineru/logs/`
3. **Compare:** Seu código com `old_code/mineru_desktop/ui/main_window.py`
4. **Reverta se necessário:** `cp src/ui/main_window.py.backup src/ui/main_window.py`

---

**📅 Criado:** 2025-11-21
**🎯 Para:** MinerU Desktop Client v1.1.0 → v1.2.0
**👤 Executor:** Próximo chat Claude
**⏱️ Duração:** 60-75 minutos

---

**🚀 Boa sorte! Todo o código e comandos estão prontos - basta seguir as fases!**
