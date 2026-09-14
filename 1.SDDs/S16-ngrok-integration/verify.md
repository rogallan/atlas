# Verify — S16 · ngrok Integration

## Evidence checklist

- [ ] Startup script execution log showing ngrok launch and successful extraction of the assigned public HTTPS URL.
- [ ] Smoke test output (`smoke_test_tunnel.py`) verifying `200 OK` on `GET /health` with `Access-Control-Allow-Origin` present.
- [ ] Streaming test output showing incremental chunk arrival over the public tunnel with `text/event-stream` media type.
- [ ] Screenshot or terminal log showing ngrok web traffic inspector (`http://localhost:4040`) capturing live requests from the external frontend.
- [ ] Verification of operational runbook (`docs/runbooks/ngrok_tunnel.md`) showing clear setup and teardown steps.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — networking path, CORS middleware, and automation scripts match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
