# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

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

[1.0.0]: https://github.com/ozp/MinerU-linux-desktop/releases/tag/v1.0.0
