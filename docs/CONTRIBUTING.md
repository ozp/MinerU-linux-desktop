# Guia de Contribuição - MinerU Desktop Client

Obrigado por considerar contribuir para o MinerU Desktop Client! Este documento fornece diretrizes e melhores práticas para contribuir com o projeto.

## Índice

- [Código de Conduta](#código-de-conduta)
- [Como Posso Contribuir?](#como-posso-contribuir)
- [Configuração do Ambiente](#configuração-do-ambiente)
- [Workflow de Desenvolvimento](#workflow-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

---

## Código de Conduta

### Nossa Promessa

No interesse de promover um ambiente aberto e acolhedor, nós, como colaboradores e mantenedores, nos comprometemos a tornar a participação em nosso projeto e comunidade uma experiência livre de assédio para todos.

### Padrões

**Comportamentos Encorajados**:
- Usar linguagem acolhedora e inclusiva
- Respeitar diferentes pontos de vista e experiências
- Aceitar críticas construtivas graciosamente
- Focar no que é melhor para a comunidade
- Mostrar empatia com outros membros da comunidade

**Comportamentos Inaceitáveis**:
- Uso de linguagem ou imagens sexualizadas
- Comentários trolling, insultos ou ataques pessoais/políticos
- Assédio público ou privado
- Publicar informações privadas de outros sem permissão
- Outras condutas consideradas inapropriadas em ambiente profissional

---

## Como Posso Contribuir?

### 1. Reportar Bugs

Encontrou um bug? Ajude-nos criando uma issue detalhada:

- Use o template de bug report
- Inclua passos claros para reproduzir
- Adicione screenshots se aplicável
- Especifique seu ambiente (OS, Python version, etc.)

### 2. Sugerir Melhorias

Tem uma ideia para tornar o projeto melhor?

- Abra uma issue descrevendo sua sugestão
- Explique por que seria útil
- Forneça exemplos de uso se possível

### 3. Melhorar Documentação

- Corrigir typos
- Adicionar exemplos
- Melhorar clareza
- Traduzir documentação

### 4. Contribuir com Código

- Corrigir bugs
- Implementar novas features
- Melhorar performance
- Adicionar testes

---

## Configuração do Ambiente

### Requisitos

- Python 3.8 ou superior
- Git
- Linux (Ubuntu/Debian recomendado)

### Setup Inicial

```bash
# 1. Fork o repositório no GitHub

# 2. Clone seu fork
git clone https://github.com/YOUR_USERNAME/MinerU-linux-desktop.git
cd MinerU-linux-desktop

# 3. Adicione o repositório original como upstream
git remote add upstream https://github.com/ozp/MinerU-linux-desktop.git

# 4. Instale dependências do sistema
./install_system_deps.sh

# 5. Crie ambiente virtual
python3 -m venv venv
source venv/bin/activate

# 6. Instale dependências Python
pip install -r requirements.txt

# 7. Instale dependências de desenvolvimento
pip install -r requirements-dev.txt
# Ou manualmente:
pip install pytest pytest-qt pytest-cov pytest-mock black flake8 mypy

# 8. Configure pre-commit hooks (opcional mas recomendado)
pip install pre-commit
pre-commit install
```

### Verificar Setup

```bash
# Executar aplicação
python main.py

# Executar testes
pytest

# Verificar linting
flake8 *.py
black --check *.py
mypy *.py
```

---

## Workflow de Desenvolvimento

### 1. Criar Branch

```bash
# Atualizar main local
git checkout main
git pull upstream main

# Criar branch para sua feature/fix
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bugfix
```

**Convenções de Nome de Branch**:
- `feature/` - Novas funcionalidades
- `fix/` - Correções de bugs
- `docs/` - Mudanças em documentação
- `refactor/` - Refatorações de código
- `test/` - Adição/modificação de testes

### 2. Fazer Mudanças

```bash
# Editar arquivos
code main.py

# Executar testes frequentemente
pytest

# Verificar linting
black *.py
flake8 *.py
```

### 3. Commit

```bash
# Adicionar mudanças
git add .

# Commit com mensagem descritiva
git commit -m "feat: adiciona suporte a drag-and-drop de arquivos"
```

**Convenção de Commits** (Conventional Commits):

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: Nova feature
- `fix`: Correção de bug
- `docs`: Mudanças em documentação
- `style`: Formatação, ponto-e-vírgula, etc (sem mudança de código)
- `refactor`: Refatoração de código
- `test`: Adição/modificação de testes
- `chore`: Manutenção, build, etc

**Exemplos**:
```bash
git commit -m "feat(ui): adiciona botão de cancelar upload"
git commit -m "fix(api): corrige erro de timeout em uploads grandes"
git commit -m "docs: atualiza README com instruções de i18n"
git commit -m "test(client): adiciona testes para MineruClient.upload_batch"
git commit -m "refactor: extrai lógica de polling para método separado"
```

### 4. Push

```bash
# Push para seu fork
git push origin feature/minha-feature
```

### 5. Manter Sincronizado

```bash
# Buscar mudanças do upstream
git fetch upstream

# Merge mudanças do main
git checkout main
git merge upstream/main

# Rebase sua branch
git checkout feature/minha-feature
git rebase main
```

---

## Padrões de Código

### Python Style Guide

Seguimos [PEP 8](https://pep8.org/) com algumas adaptações.

#### Formatação

- **Linhas**: Máximo 100 caracteres (não 79)
- **Indentação**: 4 espaços (não tabs)
- **Imports**: Ordenados alfabeticamente, agrupados
- **Strings**: Usar aspas duplas `"` por padrão

**Exemplo**:
```python
"""Module docstring."""

import os
import sys
from typing import List, Optional

from PySide6.QtWidgets import QWidget
import requests

from mineru_client import MineruClient


class MyClass:
    """Class docstring."""

    def __init__(self, param: str) -> None:
        """Initialize with param."""
        self.param = param

    def my_method(self, arg: int) -> List[str]:
        """Method docstring.

        Args:
            arg: Description of arg

        Returns:
            List of strings
        """
        result = []
        # Implementation
        return result
```

#### Docstrings

Usar **Google Style**:

```python
def function(arg1: int, arg2: str) -> bool:
    """Summary line em uma frase.

    Descrição mais detalhada se necessário. Pode ter
    múltiplas linhas.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When arg1 is negative
        KeyError: When arg2 not found

    Example:
        >>> function(5, "test")
        True
    """
    if arg1 < 0:
        raise ValueError("arg1 must be non-negative")
    return True
```

#### Type Hints

Usar type hints sempre que possível:

```python
from typing import List, Dict, Optional, Callable

def process_files(
    files: List[str],
    callback: Optional[Callable[[int], None]] = None
) -> Dict[str, str]:
    """Process files with optional callback."""
    result: Dict[str, str] = {}
    # Implementation
    return result
```

### Naming Conventions

```python
# Classes: PascalCase
class MyClass:
    pass

# Functions/Methods: snake_case
def my_function():
    pass

# Constants: UPPER_SNAKE_CASE
MAX_WORKERS = 5
API_BASE_URL = "https://api.example.com"

# Private: _leading_underscore
def _private_helper():
    pass

class MyClass:
    def __init__(self):
        self._private_attr = None

# Protected: _single_leading (por convenção)
# Dunder methods: __double__ (especiais Python)
```

### Estrutura de Arquivos

```python
"""Module docstring.

Descrição detalhada do módulo.

Example:
    from my_module import MyClass

    obj = MyClass()
    obj.do_something()
"""

# Standard library imports
import os
import sys

# Third-party imports
from PySide6.QtWidgets import QWidget
import requests

# Local imports
from mineru_client import MineruClient
from version import VERSION


# Constants
MAX_RETRIES = 3


# Classes
class MyClass:
    """Class docstring."""
    pass


# Functions
def my_function():
    """Function docstring."""
    pass


# Main execution
if __name__ == "__main__":
    main()
```

### Ferramentas

#### Black (Formatação)

```bash
# Formatar todos os arquivos
black *.py

# Verificar sem modificar
black --check *.py

# Configuração em pyproject.toml
[tool.black]
line-length = 100
target-version = ['py38']
```

#### Flake8 (Linting)

```bash
# Verificar todos os arquivos
flake8 *.py

# Configuração em .flake8
[flake8]
max-line-length = 100
exclude = .git,__pycache__,venv
ignore = E203, W503
```

#### MyPy (Type Checking)

```bash
# Verificar tipos
mypy *.py

# Configuração em mypy.ini
[mypy]
python_version = 3.8
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
```

---

## Processo de Pull Request

### 1. Antes de Submeter

**Checklist**:
- [ ] Código segue style guide
- [ ] Todos os testes passam
- [ ] Novos testes adicionados para nova funcionalidade
- [ ] Documentação atualizada
- [ ] Commit messages seguem convenção
- [ ] Branch está atualizada com main

```bash
# Verificar tudo
black *.py
flake8 *.py
pytest
```

### 2. Criar Pull Request

1. Vá ao seu fork no GitHub
2. Clique em "Pull Request"
3. Selecione sua branch
4. Preencha o template:

```markdown
## Descrição

[Descrição clara das mudanças]

## Tipo de Mudança

- [ ] Bug fix (mudança que corrige um issue)
- [ ] Nova feature (mudança que adiciona funcionalidade)
- [ ] Breaking change (fix ou feature que quebra compatibilidade)
- [ ] Documentação

## Como Foi Testado?

[Descreva os testes realizados]

## Checklist

- [ ] Meu código segue o style guide
- [ ] Realizei self-review do código
- [ ] Comentei partes complexas
- [ ] Atualizei documentação
- [ ] Minhas mudanças não geram novos warnings
- [ ] Adicionei testes
- [ ] Todos os testes passam localmente

## Screenshots (se aplicável)

[Adicione screenshots]

## Issues Relacionadas

Closes #123
```

### 3. Review Process

- Mantenedor irá revisar o código
- Pode solicitar mudanças
- Discussão via comentários
- Aprovação final

### 4. Após Merge

```bash
# Atualizar seu fork
git checkout main
git pull upstream main
git push origin main

# Deletar branch (opcional)
git branch -d feature/minha-feature
git push origin --delete feature/minha-feature
```

---

## Reportando Bugs

### Template de Bug Report

```markdown
## Descrição do Bug

[Descrição clara e concisa]

## Passos para Reproduzir

1. Vá para '...'
2. Clique em '....'
3. Role até '....'
4. Veja erro

## Comportamento Esperado

[O que deveria acontecer]

## Comportamento Atual

[O que está acontecendo]

## Screenshots

[Se aplicável, adicione screenshots]

## Ambiente

- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.10.12]
- Versão: [e.g., 1.0.1]
- Método de instalação: [AppImage/source]

## Logs/Traceback

```python
[Cole o traceback aqui]
```

## Contexto Adicional

[Qualquer outra informação relevante]
```

---

## Sugerindo Melhorias

### Template de Feature Request

```markdown
## Problema Relacionado

[Descrição do problema que esta feature resolveria]

## Solução Proposta

[Descrição clara da solução desejada]

## Alternativas Consideradas

[Outras soluções que você considerou]

## Contexto Adicional

[Screenshots, mockups, exemplos, etc.]
```

---

## Áreas para Contribuição

### Fácil (Good First Issue)

- Corrigir typos em documentação
- Adicionar testes para código existente
- Melhorar mensagens de erro
- Adicionar tooltips na UI

### Média

- Implementar novas features pequenas
- Refatorar código existente
- Melhorar tratamento de erros
- Adicionar logging

### Difícil

- Implementar features complexas
- Otimizações de performance
- Arquitetura de sistema
- Internacionalização completa

---

## Recursos para Contribuidores

### Documentação Técnica

- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura do sistema
- [API.md](API.md) - Documentação da API interna
- [TESTING.md](TESTING.md) - Guia de testes
- [PATTERNS.md](PATTERNS.md) - Padrões de código

### Ferramentas Úteis

- [PySide6 Documentation](https://doc.qt.io/qtforpython/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Documentation](https://black.readthedocs.io/)
- [Type Hints Cheat Sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

### Comunicação

- **Issues**: Para bugs e feature requests
- **Discussions**: Para perguntas e discussões gerais
- **Pull Requests**: Para contribuições de código

---

## Reconhecimento

Todos os contribuidores serão adicionados ao arquivo CONTRIBUTORS.md e reconhecidos no README.

Tipos de contribuição:
- 💻 Código
- 📖 Documentação
- 🐛 Bug reports
- 💡 Ideas
- 🎨 Design
- 🌍 Tradução

---

## Dúvidas?

Se tiver dúvidas sobre como contribuir:

1. Verifique a documentação existente
2. Procure em issues fechadas
3. Abra uma Discussion
4. Entre em contato com mantenedores

**Obrigado por contribuir! 🎉**
