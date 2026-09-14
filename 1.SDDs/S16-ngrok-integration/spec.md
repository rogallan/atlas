# Spec — S16 · ngrok Integration

> **Domain:** Integration / Infra · **Quarter:** Q3 · **Depends on:** S01 (Python Toolchain), S03 (FastAPI Gateway), S15 (React Chat)

## 1. Goal

Establish a secure, automated, and controlled tunnel using **ngrok** to expose the local FastAPI Gateway (running locally on developer machine or CI) to the React Chat frontend published externally on **Vercel**, configuring Cross-Origin Resource Sharing (CORS), environment synchronization, traffic monitoring, and operational runbooks.

## 2. Context

Per `architecture.md`, `constitution.md` (Principle 1: "Local-first"), and the lab environment documented in `PDI_ATLAS_GenAI_Banking_Copilot_PT_BR.html`, ATLAS maintains all backend processing (FastAPI, Ollama, Vector DB, MCP servers, synthetic data) in the local environment while allowing the frontend to be published externally on Vercel. ngrok acts as the secure bridge: it tunnels incoming HTTPS traffic from the internet directly to the local FastAPI port (`8000`), ensuring that the Vercel-hosted UI can communicate with the local copilot stack without opening unsecured router ports or deploying heavy infrastructure.

## 3. In scope

- ngrok configuration and automation scripts (`ngrok.yml` and CLI helper scripts).
- FastAPI CORS middleware configuration to securely accept origins from the Vercel production domain and localhost.
- Dynamic or static tunnel endpoint configuration synchronized with frontend environment variables (`VITE_API_BASE_URL`).
- HTTP security headers and ngrok inspection webhook/dashboard configuration.
- Operational runbook (`docs/runbooks/ngrok_tunnel.md`) detailing tunnel startup, authentication, CORS verification, and teardown.
- End-to-end smoke test verifying the published frontend (or Vercel preview) -> ngrok tunnel -> local FastAPI Gateway -> streamed response flow.

## 4. Out of scope

- Production cloud infrastructure deployment (AWS ECS/ALB), which is represented via Terraform in S21.
- Hosting the local backend permanently in the cloud.
- Domain certificate management (handled automatically by ngrok's SSL termination).

## 5. Requirements

- **R1. Controlled Exposure:** ngrok must bind strictly to the local FastAPI port (`http://localhost:8000`) and enforce encrypted HTTPS termination.
- **R2. CORS Configuration:** FastAPI must accept Cross-Origin requests from the designated Vercel frontend URL, allowing required methods (`GET`, `POST`, `OPTIONS`) and headers (`Content-Type`, `Authorization`, `X-Session-ID`).
- **R3. Automated Startup & URL Sync:** Provide a helper script (`scripts/start_tunnel.py` or shell script) that launches ngrok, captures the assigned public HTTPS URL via ngrok's local management API (`http://127.0.0.1:4040/api/tunnels`), and outputs instructions for configuring Vercel environment variables.
- **R4. Stream Compatibility (SSE):** The ngrok tunnel configuration must preserve unbuffered HTTP streaming for Server-Sent Events without premature buffering or chunk truncation.
- **R5. Security & Traffic Inspection:** Leverage ngrok's traffic inspection dashboard on `localhost:4040` for local debugging and audit validation, ensuring sensitive keys or credentials are not exposed in query parameters.
- **R6. Step-by-Step Runbook:** Provide a clear, actionable operational runbook documenting prerequisites, authtoken setup, tunnel launch, health checks, and troubleshooting common tunnel issues.

## 6. Acceptance criteria

- Running the tunnel startup script launches ngrok and outputs a healthy HTTPS forwarding URL.
- Invoking `GET /health` through the public ngrok HTTPS URL returns `{ "status": "ok" }` with correct CORS headers.
- The React Chat frontend (hosted on Vercel or local preview) successfully streams responses from `POST /v1/chat` through the ngrok URL.
- Operational runbook is documented and tested by executing a complete smoke test from a clean terminal.
