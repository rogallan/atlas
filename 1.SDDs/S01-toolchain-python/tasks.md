# S01 — Projeto e toolchain Python · Tarefas

Fonte: Trimestre 1 (Fundação) do PDI.

- [ ] **Criar estrutura de repositório** (`SDDs/`, `docs/`, `src/` com as
      subpastas `api/`, `agent/`, `rag/`, `mcp/`, `providers/`, `data/`
      alinhadas ao `architecture.md` de S00).
- [ ] **Escolher e configurar gerenciador de dependências** (`uv` ou `poetry`),
      com lockfile versionado; registrar a decisão como ADR.
- [ ] **Configurar lint, formatter e typing** (`ruff` + `mypy`) via
      `pyproject.toml`, com `mypy` em modo estrito em `src/`.
- [ ] **Configurar `pre-commit`** com hooks de `ruff format`, `ruff check --fix`
      e `mypy`, validado localmente.
- [ ] **Configurar ambiente de testes** (`pytest` + `pytest-asyncio` +
      `pytest-cov`), com um smoke test de exemplo passando e cobertura mínima
      inicial definida.
- [ ] **Criar `Dockerfile` base** (multi-stage) que builda a imagem da
      aplicação Python com sucesso.
- [ ] **Criar pipeline de CI mínimo** que roda lint + type check + testes a
      cada push/PR.
- [ ] **Documentar o setup local** no `README.md` (passo a passo: clonar,
      instalar dependências, ativar pre-commit, rodar testes).
