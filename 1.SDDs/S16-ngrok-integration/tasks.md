# Tasks — S16 · ngrok Integration

- [x] Create ngrok configuration file in `infra/ngrok/ngrok.yml`.
- [x] Implement CORS middleware in `src/api/middleware/cors.py` with support for Vercel production and preview domains.
- [x] Implement tunnel startup automation script in `scripts/start_tunnel.py` to launch ngrok and extract the public HTTPS URL via the local API.
- [x] Implement end-to-end tunnel smoke test in `scripts/smoke_test_tunnel.py` validating `/health`, CORS headers, and SSE streaming.
- [x] Write operational runbook `docs/runbooks/ngrok_tunnel.md` with step-by-step instructions for local backend setup, ngrok token configuration, Vercel environment sync, and troubleshooting.
- [x] Execute smoke test verifying external request flow: public ngrok URL -> local FastAPI Gateway -> SSE response stream.

## Definition of Done

- [x] All tasks above are complete and merged.
- [x] Tunnel startup script reliably boots ngrok and prints the public HTTPS forwarding URL.
- [x] CORS policy allows access from the published Vercel frontend without browser preflight errors.
- [x] SSE stream flows unbuffered across the ngrok tunnel.
- [x] Operational runbook is published in `docs/runbooks/` and verified with a clean terminal run.
