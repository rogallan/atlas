# ATLAS — Banking GenAI Copilot

Copiloto conversacional para gerente bancário: consulta conhecimento público do
Banco Central (RAG), consulta base fictícia de clientes/histórico (MCP) e executa
operações simples simuladas por ferramentas controladas.

Stack: React Chat · FastAPI · Ollama · RAG/Vector DB · MCP · Harness/Evals ·
Docker · ngrok · Terraform/AWS.

## Estrutura

- `SDDs/` — um subdiretório por item do catálogo SDD (S00 → S22), cada um com
  `spec.md`, `plan.md`, `tasks.md`, `verify.md`.
- `docs/adr/` — Architecture Decision Records.
- `docs/runbooks/` — runbooks operacionais.
- `src/api/` — FastAPI: rotas, contratos, streaming, auth simulada.
- `src/agent/` — Router, Validator/Critic, grafo do agente.
- `src/rag/` — ingestão, chunking, embeddings, retrieval.
- `src/mcp/` — MCP servers: perfil, empréstimo, seguro, consórcio, tarifas, ticket.
- `src/providers/` — adapter Ollama (LLM local).
- `src/data/` — modelos sintéticos de cliente/histórico + seed.
- `frontend/` — React Chat (publicado na Vercel).
- `infra/docker/` — docker-compose (API, MCP, Vector, Ollama).
- `infra/terraform/` — módulos AWS (network, compute, data, observability).
- `evals/` — harness, golden dataset, golden conversations, scorecards.
- `tests/` — unitários, integração, contrato e segurança.
- `ops/` — observabilidade: logs, traces, correlation ID.
