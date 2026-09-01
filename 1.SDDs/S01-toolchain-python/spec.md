# S01 — Projeto e toolchain Python

Trimestre: T1 · Categoria: Fundação
Entregável: `spec.md` + `plan.md` + `tasks.md` (deste item) + toolchain reproduzível no repositório

## 1. Objetivo

Estabelecer a fundação de engenharia do ATLAS: estrutura de repositório, ambiente
Python reprodutível, qualidade de código automatizada (lint/format/typing) e
testes, além de um pipeline de CI mínimo. Este item entrega a base sobre a qual
todo código de S02 em diante será escrito — nenhuma feature de produto deve
começar antes de S01 estar concluído.

## 2. Contexto

O ATLAS é escrito majoritariamente em Python no backend (FastAPI, Agent, RAG,
MCP, providers). Para sustentar um projeto de nível sênior ao longo de quatro
trimestres, o toolchain precisa ser decidido uma única vez, de forma consistente,
em vez de crescer organicamente e gerar dívida técnica.

Este item segue diretamente o `constitution.md` e o `architecture.md` definidos
em S00: a estrutura de pastas aqui criada deve refletir as fronteiras
Front/API/Agent/MCP/RAG/Infra já documentadas.

## 3. Escopo

1. Estrutura de repositório (`SDDs/`, `docs/`, `src/`, e subpastas de `src/`
   alinhadas à arquitetura: `api/`, `agent/`, `rag/`, `mcp/`, `providers/`, `data/`).
2. Gerenciador de dependências e ambiente virtual Python.
3. Lint, formatter e type checking (ex.: `ruff` para lint/format, `mypy` para
   tipagem estática) configurados via `pre-commit`.
4. Ambiente de testes (`pytest`) com cobertura mínima definida.
5. `Dockerfile` base para a aplicação Python.
6. Pipeline de CI mínimo (lint + type check + testes rodando em cada push/PR).

## 4. Fora de escopo

- Código de produto (rotas de API, agente, RAG, MCP) — isso começa em S02+.
- Docker Compose completo com múltiplos serviços (Ollama, Vector DB) — isso é
  tratado em S20 (Docker Local Stack); aqui só o `Dockerfile` base da aplicação.
- CI/CD de deploy em cloud — isso é tratado em T4 (S21/S22).

## 5. Decisões técnicas sugeridas

- **Gerenciador de pacotes**: `uv` ou `poetry` (decisão registrada como ADR em
  `docs/adr/`, com justificativa de escolha).
- **Versão do Python**: 3.11+ (suporte a typing moderno, performance async).
- **Lint/format**: `ruff` (substitui flake8+black+isort em uma ferramenta).
- **Type checking**: `mypy` em modo estrito nos módulos de `src/`.
- **Testes**: `pytest` + `pytest-asyncio` (o projeto usa FastAPI/async desde S03).
- **Pre-commit**: hooks de lint, format e type check rodando antes de cada commit.
- **Cobertura mínima**: definir um piso inicial (ex.: 70%) que sobe ao longo dos
  trimestres, sem travar o T1 com uma meta irrealista.

## 6. Critérios de aceite

- [ ] Estrutura de `src/` criada e alinhada ao `architecture.md` (S00).
- [ ] Ambiente Python reprodutível (lockfile versionado, `README` com passo a
      passo de setup local).
- [ ] `ruff` e `mypy` configurados e rodando sem erros no esqueleto inicial.
- [ ] `pre-commit` instalado e validado localmente.
- [ ] `pytest` configurado, com pelo menos um teste de exemplo passando e
      métrica de cobertura sendo reportada.
- [ ] `Dockerfile` base builda a imagem da aplicação com sucesso.
- [ ] Pipeline de CI mínimo executa lint + type check + testes a cada push/PR.
