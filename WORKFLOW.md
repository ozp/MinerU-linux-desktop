# Workflow para Novas Sessões - MinerU Linux Desktop

## Status Atual do Repositório

Este é um **repositório novo sem branch padrão** (main/master).
Todas as alterações são feitas em branches específicas do Claude.

## Verificação Antes de Criar PR

### ✅ Todos os Commits Estão Sincronizados

Branch atual: `claude/fix-file-reading-web-01PBcjzj5Rp4yF4VET7FHrW3`

Commits disponíveis no GitHub:
```
ea0c1d3 - Update README with automatic ZIP extraction documentation
c085a4d - Fix automatic ZIP extraction after download
bc44877 - Fix AppImage download link to point to current branch
27ae5c4 - Update README and AppImage with Portuguese language support improvements
f1cf3c1 - Fix Portuguese language support by adding model_version parameter
```

### Arquivos Modificados Nesta Sessão

1. **mineru_client.py** - Adicionado suporte a `model_version`
2. **settings_dialog.py** - Interface para seleção de modelo
3. **main.py** - Extração automática de ZIP
4. **config.ini.example** - Configuração com `model_version`
5. **README.md** - Documentação completa
6. **MinerU-x86_64.AppImage** - Rebuild (72 MB)

---

## Como Criar Pull Request no GitHub

Como o `gh` CLI não está disponível, use a interface web:

### Passo a Passo:

1. **Acesse:** https://github.com/ozp/MinerU-linux-desktop

2. **Você verá uma mensagem:**
   ```
   claude/fix-file-reading-web-01PBcjzj5Rp4yF4VET7FHrW3 had recent pushes
   [Compare & pull request]
   ```

3. **Clique em "Compare & pull request"**

4. **Preencha o Pull Request:**

   **Título:**
   ```
   Fix Portuguese language support and automatic ZIP extraction
   ```

   **Descrição:**
   ```markdown
   ## Problemas Resolvidos

   1. **Suporte a Português**: Modelo VLM tinha dificuldades com texto em português
      - Textos apareciam corrompidos: "içãç b iv ç c d iibiçãaçãçã"

   2. **Extração de ZIP**: Arquivos baixados ficavam como ZIP ao invés de pastas extraídas
      - Usuários tinham que extrair manualmente

   ## Mudanças Implementadas

   ### 1. Suporte a Modelo Pipeline/VLM (mineru_client.py, settings_dialog.py)
   - ✅ Adicionado parâmetro `model_version` com opções Pipeline/VLM
   - ✅ Modelo Pipeline configurado como padrão (melhor para português)
   - ✅ Parâmetro `language` só enviado quando usar Pipeline
   - ✅ Interface atualizada com seleção de modelo e avisos visuais

   ### 2. Extração Automática de ZIP (main.py)
   - ✅ Arquivos baixados são automaticamente extraídos para pastas
   - ✅ Pasta nomeada com o nome do arquivo original
   - ✅ ZIP removido após extração bem-sucedida

   ### 3. Documentação (README.md)
   - ✅ Seção "Suporte a Idiomas" com explicações detalhadas
   - ✅ Instruções sobre quando usar cada modelo
   - ✅ Problema conhecido do VLM documentado
   - ✅ Exemplos de configuração atualizados

   ### 4. AppImage Atualizado
   - ✅ Reconstruído com todas as correções (v1.0.1, 72MB)
   - ✅ Link de download atualizado no README

   ## Configuração Recomendada para Português

   - **MinerU Model:** Pipeline (Legado - Melhor para Português)
   - **Select OCR Language:** Portuguese (pt)

   ## Commits

   - `ea0c1d3` - Update README with automatic ZIP extraction documentation
   - `c085a4d` - Fix automatic ZIP extraction after download
   - `bc44877` - Fix AppImage download link to point to current branch
   - `27ae5c4` - Update README and AppImage with Portuguese language support improvements
   - `f1cf3c1` - Fix Portuguese language support by adding model_version parameter

   ## Testes

   - [x] Build do AppImage concluído com sucesso
   - [x] Código Python sem erros de sintaxe
   - [x] Documentação atualizada e consistente
   - [x] Configuração de exemplo atualizada
   ```

5. **Clique em "Create pull request"**

---

## Para Novas Sessões: Como Criar Nova Branch

### Cenário 1: Após Merge do PR Atual

Quando o PR da branch `claude/fix-file-reading-web-01PBcjzj5Rp4yF4VET7FHrW3` for aceito:

```bash
# 1. Sincronizar com o remote
git fetch origin

# 2. Se uma branch main/master for criada após o merge
git checkout main  # ou master
git pull origin main

# 3. Criar nova branch para próximo trabalho
git checkout -b claude/nova-feature-[SESSION_ID]

# 4. Trabalhar normalmente
# ... fazer alterações ...

# 5. Commit e push
git add .
git commit -m "Descrição das mudanças"
git push -u origin claude/nova-feature-[SESSION_ID]
```

### Cenário 2: Repositório Ainda Sem Branch Padrão

Se o repositório continuar sem main/master:

```bash
# 1. Listar branches existentes
git branch -r

# 2. Verificar qual branch tem mais commits (base mais recente)
git log --oneline --graph --all -10

# 3. Criar nova branch a partir da branch mais atualizada
git fetch origin
git checkout -b claude/nova-feature-[SESSION_ID] origin/claude/fix-file-reading-web-01PBcjzj5Rp4yF4VET7FHrW3

# 4. Trabalhar normalmente
# ... fazer alterações ...

# 5. Commit e push
git add .
git commit -m "Descrição das mudanças"
git push -u origin claude/nova-feature-[SESSION_ID]
```

### Cenário 3: Criar Branch Padrão Manualmente

Se quiser criar uma branch `main` como padrão:

```bash
# 1. A partir da branch atual (que tem todo o código)
git checkout claude/fix-file-reading-web-01PBcjzj5Rp4yF4VET7FHrW3

# 2. Criar branch main localmente
git checkout -b main

# 3. Fazer push da branch main
git push -u origin main

# 4. No GitHub, vá em Settings > Branches > Default branch
#    e configure 'main' como branch padrão

# 5. Agora pode trabalhar normalmente com main como base
git checkout main
git pull origin main
git checkout -b claude/nova-feature-[SESSION_ID]
```

---

## 🏷️ Versionamento Semântico (Tags e Releases)

### O que é Versionamento Semântico?

Usamos o formato **v0.0.1**, **v0.0.2**, etc. (também conhecido como SemVer):

```
v MAJOR . MINOR . PATCH
  │       │       │
  │       │       └─ Correções de bugs (bug fixes)
  │       └───────── Novas funcionalidades (features)
  └───────────────── Mudanças incompatíveis (breaking changes)
```

**Exemplos:**
- `v1.0.0` → Primeira versão estável
- `v1.1.0` → Adicionou nova funcionalidade
- `v1.1.1` → Corrigiu um bug
- `v2.0.0` → Mudança que quebra compatibilidade

### Como Criar uma Nova Versão (Release)

#### 1. Via Interface do GitHub (Recomendado)

**Passo a Passo:**

1. Acesse: https://github.com/ozp/MinerU-linux-desktop/releases

2. Clique em **"Create a new release"**

3. Preencha:
   - **Tag version**: `v1.0.0` (ou a versão desejada)
   - **Target**: `main` (ou a branch desejada)
   - **Release title**: Mesmo que a tag (ex: `v1.0.0`)
   - **Description**: O que mudou nessa versão

4. Se tiver AppImage novo:
   - Arraste o arquivo `MinerU-x86_64.AppImage` para a área de anexos
   - Isso cria um link permanente para download

5. Clique em **"Publish release"**

**Exemplo de Descrição:**

```markdown
## 🎉 Release v1.0.0

### Novidades
- ✅ Suporte completo a português (modelo Pipeline)
- ✅ Extração automática de arquivos ZIP
- ✅ Interface de seleção de modelo VLM/Pipeline
- ✅ AppImage otimizado (72MB)

### Correções
- 🐛 Textos em português não aparecem mais corrompidos
- 🐛 Downloads são extraídos automaticamente

### Como Usar
Baixe o AppImage, dê permissão de execução e rode!

```bash
chmod +x MinerU-x86_64.AppImage
./MinerU-x86_64.AppImage
```

### Configuração Recomendada
- **Model**: Pipeline (Legado)
- **Language**: Portuguese (pt)
```

#### 2. Via Git (Linha de Comando)

Se preferir criar tags localmente:

```bash
# 1. Certifique-se de estar na branch main atualizada
git checkout main
git pull origin main

# 2. Criar tag anotada (recomendado)
git tag -a v1.0.0 -m "Release v1.0.0 - Portuguese support and auto ZIP extraction"

# 3. Fazer push da tag
git push origin v1.0.0

# 4. Ver todas as tags
git tag -l

# 5. Depois vá no GitHub criar o Release associado a essa tag
```

### Histórico de Versões (Exemplo)

| Versão | Data | Descrição |
|--------|------|-----------|
| v1.0.1 | 2024-XX-XX | Correção: Bug na extração de ZIP |
| v1.0.0 | 2024-XX-XX | Primeira versão: Suporte a português + auto-extract |
| v0.1.0 | 2024-XX-XX | Beta: Interface básica |

### Quando Criar uma Nova Versão?

- **Sempre que houver mudanças importantes** mergeadas na `main`
- **Quando reconstruir o AppImage** com novas funcionalidades
- **Após correção de bugs críticos**

### Comandos Úteis para Tags

```bash
# Listar todas as tags
git tag

# Ver detalhes de uma tag
git show v1.0.0

# Deletar tag local
git tag -d v1.0.0

# Deletar tag remota (cuidado!)
git push origin --delete v1.0.0

# Fazer checkout de uma versão específica
git checkout v1.0.0
```

---

## Comandos Úteis para Verificação

```bash
# Ver todas as branches (local e remote)
git branch -a

# Ver status de sincronização
git status

# Ver últimos commits
git log --oneline -10

# Ver diferenças com remote
git fetch origin
git diff origin/[branch-name]

# Ver histórico em grafo
git log --oneline --graph --all -20
```

---

## Checklist Antes de Criar PR

- [ ] Todos os commits estão no remote (`git push` completo)
- [ ] `git status` mostra "nothing to commit, working tree clean"
- [ ] `git diff origin/[branch]` não mostra diferenças
- [ ] Documentação atualizada (README.md, etc.)
- [ ] AppImage reconstruído se houver mudanças no código
- [ ] Commits têm mensagens descritivas

---

## Observações Importantes

1. **Este repositório não tem branch padrão ainda** - trabalhe sempre criando branches específicas

2. **AppImage tem 72MB** - GitHub vai avisar sobre arquivo grande, mas está OK

3. **Session ID** - Cada branch do Claude tem um ID único no final (ex: 01PBcjzj5Rp4yF4VET7FHrW3)

4. **PR via Web** - Use sempre a interface web do GitHub para criar PRs, pois `gh` CLI não está disponível

5. **Link direto para criar PR:**
   ```
   https://github.com/ozp/MinerU-linux-desktop/pull/new/[nome-da-branch]
   ```

---

## Resumo dos Arquivos Importantes

```
MinerU-linux-desktop/
├── main.py                     # Interface principal (modificado)
├── mineru_client.py            # Cliente API (modificado)
├── settings_dialog.py          # Diálogo configurações (modificado)
├── config.ini.example          # Exemplo config (modificado)
├── README.md                   # Documentação (modificado)
├── MinerU-x86_64.AppImage      # Executável (reconstruído)
├── build_appimage.sh           # Script de build
├── requirements.txt            # Dependências Python
└── WORKFLOW.md                 # Este arquivo
```

---

## Branches Disponíveis no Repositório

```
origin/claude/add-appimage-download-01QHvzyC7JoJurCxyVFXJesM
origin/claude/add-repo-info-01Wrjx3xjDZA4bK6PbQR7H8X
origin/claude/fix-download-links-01A7uu7FhWZYDYCPo2uUMG3A
origin/claude/fix-file-reading-web-01PBcjzj5Rp4yF4VET7FHrW3  ← ATUAL
origin/claude/fix-file-upload-api-01AfoEp2LNRfo9PA9NoU4DnB
origin/claude/fix-pyside6-import-01X9F9uGR9D9HuQRA4yRfVUH
origin/claude/fix-qt-plugin-error-014szein3YXC8NBVfBwtWAet
origin/claude/fix-zip-structure-01W4oB9Eu61wYXb7acWAeU14
```
