# Plan — S03 · FastAPI Gateway

## 1. Approach

Build the Gateway as a thin, well-contracted layer: define the OpenAPI schema first, implement
endpoints against stubbed downstream calls, then wire in streaming and error handling.

## 2. Key interfaces

- `GET /health` → `{status: "ok"}`.
- `POST /v1/sessions` → creates and returns a `session_id`.
- `POST /v1/chat` → body `{session_id, message}`; response is a Server-Sent Events (SSE) stream of
  message chunks, terminated by a final `done` event.
- Error responses follow a single shape: `{error: {code, message, details?}}`.

## 3. Authentication (simulated)

A static bearer token (configured via environment variable) is required on `/v1/chat` and
`/v1/sessions`. This is explicitly a simulation, not a production-grade auth system — documented as
such in the OpenAPI spec and README.

## 4. Streaming implementation

Use FastAPI's `StreamingResponse` with `text/event-stream` media type. Each chunk from the
(eventually agent-backed) response generator is flushed as it becomes available.

## 5. Test strategy

- **Integration tests** using FastAPI's `TestClient` for each endpoint (happy path + invalid
  payloads + missing/invalid auth token).
- **Streaming test** asserting that chunks arrive incrementally, not all at once.
- **Contract test** validating the OpenAPI schema stays in sync with the implementation.

## 6. Risks & mitigations

- **Risk:** streaming is hard to test reliably. **Mitigation:** use an async test client that reads
  the stream chunk by chunk with timeouts.
- **Risk:** the Gateway's contract changes as later phases (S05, S14) are built. **Mitigation:**
  version the OpenAPI schema and treat breaking changes as requiring a new ADR.
