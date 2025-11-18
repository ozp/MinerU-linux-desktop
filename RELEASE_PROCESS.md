# Processo de Release Automatizado

Este documento descreve o sistema automatizado para criar releases do MinerU Desktop Client, garantindo que o README e o AppImage sejam sempre atualizados de forma consistente.

## Visão Geral

O sistema de release automatizado garante que:
- ✅ A versão seja atualizada em todos os lugares necessários
- ✅ O AppImage seja reconstruído com a nova versão
- ✅ O CHANGELOG seja atualizado automaticamente
- ✅ Um commit e tag Git sejam criados
- ✅ O processo seja consistente e livre de erros manuais

## Arquivo de Versão Central

Todo o sistema é baseado no arquivo **`version.py`**, que contém a versão única e verdadeira da aplicação:

```python
VERSION = "1.0.0"
```

Este arquivo é usado por:
- `build_appimage.sh` - para nomear o AppImage
- `main.py` - para exibir a versão na interface
- `release.sh` - para gerenciar releases

## Como Fazer uma Release

### Script de Release Automatizado

Use o script `release.sh` para criar uma nova release:

```bash
./release.sh <tipo_versao> [descrição]
```

### Tipos de Versão

Seguindo [Semantic Versioning](https://semver.org/lang/pt-BR/):

#### 1. Patch (x.y.Z) - Correções de Bugs

```bash
./release.sh patch "Correção de bug na interface de upload"
```

Use para:
- Correções de bugs
- Pequenas melhorias
- Atualizações de documentação

**Exemplo**: 1.0.0 → 1.0.1

#### 2. Minor (x.Y.0) - Novas Funcionalidades

```bash
./release.sh minor "Adicionado suporte para arquivos Excel"
```

Use para:
- Novas funcionalidades
- Melhorias significativas
- Mudanças compatíveis com versões anteriores

**Exemplo**: 1.0.0 → 1.1.0

#### 3. Major (X.0.0) - Breaking Changes

```bash
./release.sh major "Nova arquitetura com breaking changes"
```

Use para:
- Mudanças incompatíveis com versões anteriores
- Redesign completo
- Remoção de funcionalidades antigas

**Exemplo**: 1.0.0 → 2.0.0

#### 4. Custom - Versão Customizada

```bash
./release.sh custom 2.5.0 "Release especial com nova versão customizada"
```

Use para:
- Casos especiais que não seguem o incremento automático
- Sincronização com numeração específica

## O Que o Script Faz

Quando você executa `./release.sh`, o script automaticamente:

### 1. Atualiza a Versão (`version.py`)
```python
# Antes
VERSION = "1.0.0"

# Depois (exemplo: patch)
VERSION = "1.0.1"
```

### 2. Reconstrói o AppImage
- Executa `build_appimage.sh`
- Cria `MinerU-<versão>-x86_64.AppImage`
- Atualiza o symlink `MinerU-x86_64.AppImage`

### 3. Atualiza o CHANGELOG
Adiciona automaticamente uma nova entrada:

```markdown
## [1.0.1] - 2025-11-18

### Descrição
Correção de bug na interface de upload

### Mudanças
- AppImage atualizado para versão 1.0.1
- README atualizado com informações da versão 1.0.1
```

### 4. Cria Commit Git
```bash
git commit -m "Release version 1.0.1

Correção de bug na interface de upload

- Versão atualizada para 1.0.1
- AppImage reconstruído
- CHANGELOG atualizado
"
```

### 5. Cria Tag Git
```bash
git tag -a "v1.0.1" -m "Version 1.0.1
Correção de bug na interface de upload"
```

### 6. Mostra Próximos Passos
O script informa os comandos necessários para fazer push:
```bash
git push origin <branch>
git push origin v1.0.1
```

## Workflow Completo

### Exemplo Prático: Corrigir um Bug

```bash
# 1. Faça as correções no código
vim main.py

# 2. Teste as mudanças
python main.py

# 3. Crie a release (incrementa patch: 1.0.0 → 1.0.1)
./release.sh patch "Corrigido bug no upload de múltiplos arquivos"

# 4. O script fará automaticamente:
#    - Atualizar version.py
#    - Reconstruir AppImage
#    - Atualizar CHANGELOG
#    - Criar commit
#    - Criar tag

# 5. Fazer push (seguir instruções do script)
git push origin claude/update-appimage-readme-013sLYn7urBgqqK1xjTR8kFs
git push origin v1.0.1
```

## Arquivos Gerenciados Automaticamente

O sistema gerencia automaticamente:

| Arquivo | O Que é Atualizado |
|---------|-------------------|
| `version.py` | Número da versão |
| `MinerU-<versão>-x86_64.AppImage` | AppImage versionado |
| `MinerU-x86_64.AppImage` | Symlink para última versão |
| `CHANGELOG.md` | Histórico de mudanças |
| Git tags | Tags de versão (v1.0.0, etc) |

## Vantagens do Sistema

### ✅ Consistência
- Uma única fonte de verdade para a versão (`version.py`)
- Todos os arquivos são atualizados automaticamente
- Sem discrepâncias entre versões

### ✅ Automação
- Um único comando faz todo o processo
- Reduz erros manuais
- Processo padronizado

### ✅ Rastreabilidade
- CHANGELOG automático
- Commits descritivos
- Tags Git para cada versão

### ✅ Facilidade
- Não precisa lembrar de atualizar múltiplos arquivos
- Processo claro e documentado
- Feedback visual de cada etapa

## Resolução de Problemas

### Erro: "AppImage build failed"

Se o build do AppImage falhar:
```bash
# Execute manualmente para ver o erro completo
./build_appimage.sh
```

### Erro: "Git commit failed"

Verifique se há mudanças não commitadas:
```bash
git status
```

### Reverter uma Release

Se precisar reverter:
```bash
# Reverter o commit
git reset --hard HEAD~1

# Remover a tag
git tag -d v1.0.1

# Restaurar version.py manualmente ou fazer checkout
git checkout HEAD~1 -- version.py
```

## Fluxo de Desenvolvimento Recomendado

```
1. Desenvolver funcionalidade/correção
   ↓
2. Testar localmente
   ↓
3. Executar ./release.sh <tipo> "descrição"
   ↓
4. Revisar as mudanças (git log, git diff)
   ↓
5. Fazer push do branch e da tag
   ↓
6. Criar Pull Request (se necessário)
   ↓
7. Criar GitHub Release (opcional)
```

## Integração com GitHub Releases

Após fazer push da tag, você pode criar uma GitHub Release:

```bash
# Usando gh CLI (se disponível)
gh release create v1.0.1 \
  --title "Version 1.0.1" \
  --notes "$(git tag -l --format='%(contents)' v1.0.1)" \
  MinerU-1.0.1-x86_64.AppImage

# Ou manualmente via GitHub web interface
# https://github.com/ozp/MinerU-linux-desktop/releases/new
```

## Checklist de Release

Antes de fazer uma release, verifique:

- [ ] Todas as mudanças estão testadas
- [ ] Testes estão passando
- [ ] Documentação está atualizada
- [ ] Escolheu o tipo de versão correto (patch/minor/major)
- [ ] Escreveu uma descrição clara das mudanças
- [ ] Revisou o CHANGELOG gerado
- [ ] Fez push do branch e da tag
- [ ] Criou GitHub Release (se aplicável)

## Perguntas Frequentes

### Posso editar o CHANGELOG depois?

Sim! O CHANGELOG.md pode ser editado manualmente se necessário. O script apenas adiciona uma entrada base, você pode melhorá-la.

### E se eu esquecer de fazer release?

Não há problema! Você pode fazer a release a qualquer momento. O sistema é flexível.

### Preciso fazer release para toda mudança?

Não. Faça releases quando tiver um conjunto significativo de mudanças ou correções importantes.

### Como atualizar apenas o AppImage sem mudar a versão?

```bash
# Apenas reconstruir o AppImage sem release
./build_appimage.sh
```

### Posso pular etapas do processo?

Não é recomendado, mas se precisar:
- Para apenas atualizar versão: edite `version.py`
- Para apenas construir AppImage: execute `build_appimage.sh`
- Para processo completo: use `release.sh`

## Suporte

Se encontrar problemas ou tiver sugestões para melhorar o processo de release, abra uma issue no GitHub.
