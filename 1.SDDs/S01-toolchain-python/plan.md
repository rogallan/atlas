# S01 — Projeto e toolchain Python · Plano técnico

## 1. Abordagem

Trabalho em três blocos sequenciais: (1) estrutura de pastas e ambiente, (2)
qualidade automatizada (lint/format/typing/pre-commit), (3) testes + Docker + CI.
Cada bloco termina com uma verificação rápida antes de seguir para o próximo.

## 2. Bloco 1 — Estrutura e ambiente

```
atlas/
├── src/
│   ├── api/          # (populado a partir de S03)
│   ├── agent/         # (populado a partir de S05/S14)
│   ├── rag/            # (populado a partir de S06/S07)
│   ├── mcp/             # (populado a partir de S08+)
│   ├── providers/        # (populado a partir de S04)
│   └── data/               # (populado a partir de S02)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── pyproject.toml   # dependências, metadata, config de ruff/mypy/pytest
├── uv.lock (ou poetry.lock)
├── Dockerfile
└── .pre-commit-config.yaml
```

Cada subpasta de `src/` recebe um `__init__.py` vazio nesta etapa — o conteúdo
real chega junto com o item do catálogo correspondente (S02 → S14).

## 3. Bloco 2 — Qualidade automatizada

- `pyproject.toml` centraliza a configuração de `ruff` (lint + format) e `mypy`
  (type checking estrito para tudo dentro de `src/`).
- `.pre-commit-config.yaml` roda, nesta ordem: `ruff format`, `ruff check --fix`,
  `mypy`. Falha em qualquer etapa bloqueia o commit.
- Registrar a escolha do gerenciador de pacotes (`uv` vs `poetry`) como ADR em
  `docs/adr/0001-gerenciador-de-pacotes.md`, com prós/contras considerados.

## 4. Bloco 3 — Testes, Docker e CI

- `pytest.ini` (ou seção em `pyproject.toml`) configurando `pytest-asyncio` em
  modo automático, e `pytest-cov` para métrica de cobertura.
- Um teste de exemplo (`tests/unit/test_setup.py`) que apenas confirma que o
  pacote importa corretamente — serve de smoke test do ambiente.
- `Dockerfile` multi-stage: stage de build instala dependências, stage final
  copia apenas o necessário para produção (imagem enxuta).
- CI mínimo (GitHub Actions ou equivalente): um workflow que roda em push/PR
  com os passos `ruff check`, `mypy`, `pytest --cov`.

## 5. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Typing estrito demais travar velocidade no início do projeto | Começar com `mypy` em modo estrito só em `src/`, não em `tests/`; revisar rigor a cada trimestre |
| Estrutura de pastas não escalar quando MCP/Agent crescerem | Estrutura já reflete `architecture.md` (S00); qualquer novo módulo deve ser justificado contra essa arquitetura |
| CI ficar lento e desincentivar commits frequentes | CI mínimo roda só lint+type+testes unitários; testes de integração/contrato pesados ficam fora do CI de PR nesta fase |

## 6. Saída esperada

Repositório com esqueleto de `src/`, `pyproject.toml`, `.pre-commit-config.yaml`,
`Dockerfile`, `tests/` com smoke test passando, e workflow de CI mínimo
executando com sucesso.
