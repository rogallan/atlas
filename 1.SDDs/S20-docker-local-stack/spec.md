# Spec — S20 · Docker Local Stack

> **Domain:** Platform & DevOps · **Quarter:** Q3 · **Depends on:** S01 (Python Toolchain), S03 (FastAPI Gateway), S04 (Ollama Provider), S06/S07 (Vector DB/RAG), S08–S13 (MCP Servers), S15 (React Chat)

## 1. Goal

Provide a complete, reproducible, and containerized multi-service local development and testing environment via Docker Compose, orchestrating the FastAPI Gateway, Ollama LLM provider, Vector Store/DB, typed MCP servers, and optional local React frontend, complete with automated health checks, persistent volume management, environment variable templating, and operational runbooks.

## 2. Context

Per `architecture.md`, `constitution.md` (Principle 1: "Local-first"), and the PDI catalog in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, developing and running ATLAS must not depend on cloud vendors. While developers can run individual Python processes natively, a Senior-level software system requires a single command (`docker compose up`) that boots the entire integrated stack deterministically. This guarantees that new team members, local smoke testers, or evaluation runners can spin up identical environments with zero drift.

## 3. In scope

- Multi-service Docker Compose architecture (`infra/docker/docker-compose.yml`):
  - `gateway`: FastAPI backend (API, Agent Graph, Security, Observability).
  - `ollama`: Local LLM and embedding server with persistent model cache volume.
  - `vector-db`: Persistent local vector database container (e.g. Qdrant / Chroma).
  - `mcp-servers`: Containerized MCP domain services (Customer, Loan, Insurance, Consortium, Tariff, Ticket).
  - `frontend` (optional profile): Local containerized React Chat for offline testing when Vercel/ngrok is not desired.
- Production-grade containerization (`Dockerfile` for backend and frontend using multi-stage builds).
- Health check definitions (`healthcheck`) and service dependency ordering (`depends_on` with `condition: service_healthy`).
- Named persistent volumes for models (`ollama_data`), vector storage (`vector_data`), and synthetic fixtures (`customer_data`).
- Environment variable configuration (`.env.example` with documented defaults).
- Automated stack smoke test script (`scripts/smoke_test_docker.py`) validating multi-service startup and end-to-end connectivity.
- Operational runbook (`docs/runbooks/docker_local_stack.md`).

## 4. Out of scope

- Production cloud Kubernetes (EKS) or ECS manifests (AWS cloud infrastructure is modeled via Terraform in S21).
- GPU hardware driver installation on the host (the Compose stack detects NVIDIA GPU pass-through if present, but defaults to CPU support).
- Real secrets manager integration (uses local `.env` configuration).

## 5. Requirements

- **R1. Single-Command Reproducibility:** The full local stack must boot and become operational with `docker compose up -d` without manual intermediate steps.
- **R2. Multi-Stage Container Builds:** The backend `Dockerfile` must use multi-stage builds, minimizing image size, stripping build dependencies, and running as a non-root user (`appuser`).
- **R3. Explicit Service Health Checks:** Every service must declare a health check (`/health` endpoint or CLI ping). Dependent services must wait for dependencies to be healthy before starting up.
- **R4. Persistent Storage:** Ollama downloaded models and Vector Store indices must be stored in named Docker volumes, ensuring data survives container restarts and teardowns.
- **R5. Automated Model Pulling:** Include an initialization script/container or health check hook that ensures the required Ollama models (e.g. `llama3.2:3b`, `nomic-embed-text`) are pulled automatically if missing.
- **R6. Port Isolation & Network Bridge:** Run all services in a dedicated user-defined Docker bridge network (`atlas-network`), exposing only necessary ingress ports (FastAPI `8000`, Frontend `5173`, Ollama `11434`) to the host.

## 6. Acceptance criteria

- `docker compose up -d` executes cleanly and all containers reach `healthy` status within the configured timeout.
- Running the smoke test script (`scripts/smoke_test_docker.py`) against the running containers verifies that Gateway, Ollama, Vector DB, and MCP tools respond successfully.
- Container teardown (`docker compose down`) followed by restart preserves previously indexed vector data and downloaded LLM models.
- Backend and frontend images build without security vulnerabilities or root privileges.
- Operational runbook (`docs/runbooks/docker_local_stack.md`) is documented and verified.
