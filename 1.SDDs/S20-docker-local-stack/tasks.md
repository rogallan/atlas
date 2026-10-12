# Tasks — S20 · Docker Local Stack

- [x] Create multi-stage backend container definition in `infra/docker/Dockerfile.backend` (non-root `appuser`, optimized layers).
- [x] Create multi-stage frontend container definition in `infra/docker/Dockerfile.frontend` (Nginx + static build / Next.js multi-stage).
- [x] Create Docker Compose file in `infra/docker/docker-compose.yml` with health checks, network bridge, and volume mounts.
- [x] Create environment variable template in `infra/docker/.env.example`.
- [x] Implement Ollama model initialization script in `infra/docker/init_ollama.sh`.
- [x] Implement automated Docker smoke test script in `scripts/smoke_test_docker.py` validating container health and end-to-end connectivity.
- [x] Write operational runbook in `docs/runbooks/docker_local_stack.md` detailing startup, teardown, persistence validation, and GPU configuration.
- [x] Execute smoke test verifying full stack startup and persistence across container restarts.

## Definition of Done

- All tasks above are complete and merged.
- `docker compose up -d` boots all containers into healthy state with a single command.
- Multi-stage Dockerfiles build without security issues and run as unprivileged users.
- Model downloads and vector store collections persist across container restarts.
- Automated smoke test (`scripts/smoke_test_docker.py`) passes cleanly.
- Operational runbook is documented and verified.
