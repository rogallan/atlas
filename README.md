# ATLAS — Banking GenAI Copilot

Copiloto conversacional para gerente bancário: consulta conhecimento público do
Banco Central (RAG), consulta base fictícia de clientes/histórico (MCP) e executa
operações simples simuladas por ferramentas controladas.

Stack: React Chat · FastAPI · Ollama · RAG/Vector DB · MCP · Harness/Evals ·
Docker · ngrok · Terraform/AWS · uv · Ruff · Mypy · Pytest.

Token Simulado: atlas-simulated-token-2026

---

## 🏛️ Governança & Arquitetura

O projeto é guiado pelas decisões e diretrizes documentadas em:
- [Constituição do Projeto (`constitution.md`)](file:///c:/Users/rogall/source/repos/atlas/1.SDDs/constitution.md) — Princípios inegociáveis (Local-first, Security by default, 100% synthetic data, etc.).
- [Arquitetura do Sistema (`architecture.md`)](file:///c:/Users/rogall/source/repos/atlas/1.SDDs/architecture.md) — Os 6 boundaries (Front, API, Agent, MCP, RAG, Infra).
- [Architecture Decision Records (`8.docs/adr/`)](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr) — Decisões técnicas fundamentadas (ex: [ADR-0001: uv](file:///c:/Users/rogall/source/repos/atlas/8.docs/adr/0001-package-manager.md)).

---

## 📂 Estrutura do Repositório

- `1.SDDs/` — Especificações e planos de entrega (S00 → S22), cada uma com `spec.md`, `plan.md`, `tasks.md`, `verify.md`.
- `2.src/`
  - `api/` — FastAPI: rotas, contratos OpenAPI, streaming SSE, auth simulada.
  - `agent/` — Router de intenção, nó Validator/Critic, orquestração.
  - `rag/` — Ingestão, chunking, embeddings e retrieval.
  - `mcp/` — Servidores MCP: customer, loan, insurance, consortium, tariff, ticket.
  - `providers/` — Adapter para LLM local (Ollama).
  - `data/` — Modelos de dados sintéticos e fixtures.
- `3.frontend/` — Interface conversacional React Chat.
- `4.tests/` — Testes unitários (`unit/`), integração (`integration/`) e contrato (`contract/`).
- `5.infra/` — Docker Compose local e módulos Terraform para AWS.
- `6.ops/` — Observabilidade: logs estruturados, tracing e métricas.
- `7.evals/` — Harness de avaliação, golden datasets e scorecards GenAI.
- `8.docs/` — ADRs e runbooks operacionais.

---

## 🚀 Setup Local de Desenvolvimento (S01 Toolchain)

### Pré-requisitos
- **Python 3.11+**
- **uv** (gerenciador de dependências e ambiente) instalado:
  ```bash
  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

### 1. Clonar e Instalar Dependências
```bash
# Sincroniza o ambiente e instala dependências de desenvolvimento
uv sync --all-extras
```

### 2. Ativar Hooks de Pre-commit
```bash
uv run pre-commit install
```

### 3. Executar Verificações de Qualidade
```bash
# Linter e formatação (Ruff)
uv run ruff check
uv run ruff format --check

# Checagem estrita de tipos (Mypy)
uv run mypy
```

### 4. Executar Testes Automatizados e Cobertura
```bash
uv run pytest
```

### 5. Construir a Imagem Docker da Aplicação
```bash
docker build -t atlas-banking-copilot:latest .
```

### 6. Executar o Servidor FastAPI Gateway (S03)
```bash
uv run uvicorn api.main:app --reload --port 8000
```
- **Documentação Interativa (Swagger):** http://localhost:8000/docs
- **Documentação Alternativa (ReDoc):** http://localhost:8000/redoc
- **Contrato OpenAPI:** http://localhost:8000/openapi.json
