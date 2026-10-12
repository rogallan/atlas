# ADR 0011: Ingress & Secure Tunneling via Ngrok Static Domain

## Status
Accepted

## Date
2026-10-11

## Context
Per `1.SDDs/S16-ngrok-integration/spec.md`, the relationship manager web frontend is hosted on the Vercel edge network (HTTPS), while the LLM engine (Ollama) and FastAPI Gateway run on the developer workstation (Local-First).
Problem: How can a public web application securely connect to a local backend without requiring port forwarding, static public IP addresses, or exposing insecure HTTP ports?

## Decision
Selected **Ngrok Static Domain Tunneling**:
1. **Static Ingress URL:** Configured a persistent custom static domain (`atlas-gateway.ngrok-free.app`), eliminating the need to update frontend environment variables on every restart.
2. **Deterministic Tunnel Automation:**
   - Implemented `scripts/start_tunnel.py` using `pyngrok` to start, monitor, and maintain the tunnel connection.
   - Built an automated smoke test suite (`scripts/smoke_test_tunnel.py`) to verify end-to-end SSL handshake, CORS negotiation, and latency (< 500ms).
3. **Security Headers & CORS:** Configured FastAPI to whitelist the Ngrok domain, validating preflight `OPTIONS` requests and injecting secure transport headers.

## Consequences
- **Positive:**
  - Frictionless hybrid setup: Local-first privacy and zero-cloud LLM costs combined with global Vercel cloud accessibility.
  - Zero router/firewall configuration required.
  - TLS termination handled automatically at the Ngrok edge.
- **Negative / Mitigations:**
  - Free tier limits on bandwidth and concurrent connections.
  - Completely sufficient for demonstrations, portfolio showcases, and local engineering testing.
