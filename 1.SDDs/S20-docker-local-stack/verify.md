# Verify — S20 · Docker Local Stack

## Evidence checklist

- [ ] Command output of `docker compose build` verifying multi-stage build success for backend and frontend images.
- [ ] Command output of `docker compose ps` showing all containers (`atlas-gateway`, `atlas-ollama`, `atlas-vector-db`) in `(healthy)` state.
- [ ] Smoke test output (`python scripts/smoke_test_docker.py`) demonstrating end-to-end connectivity across Gateway, Ollama, and Vector DB.
- [ ] Container security inspection verifying that the backend process runs as non-root user `appuser`.
- [ ] Persistence verification evidence showing that models in `ollama_models` and indices in `vector_data` survive `docker compose down` and subsequent `docker compose up`.
- [ ] Operational runbook verification (`docs/runbooks/docker_local_stack.md`) tested by spinning up the stack from a clean clone.

## Sign-off

- [ ] Reviewed against `spec.md` — all functional requirements (R1–R6) and acceptance criteria satisfied.
- [ ] Reviewed against `plan.md` — container topology, volume bindings, and health check definitions match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
