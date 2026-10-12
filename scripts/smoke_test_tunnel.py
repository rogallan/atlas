"""End-to-end smoke test validating health, CORS, and SSE streaming over ngrok or local tunnel (S16)."""

import argparse
import sys
from typing import Any
import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def get_active_ngrok_url() -> str | None:
    """Fetch public URL from local ngrok inspector if available."""
    try:
        res = httpx.get("http://127.0.0.1:4040/api/tunnels", timeout=1.0)
        if res.status_code == 200:
            data: dict[str, Any] = res.json()
            for t in data.get("tunnels", []):
                p_url: str = t.get("public_url", "")
                if p_url.startswith("https://"):
                    return p_url
    except Exception:
        pass
    return None


def run_smoke_test(base_url: str) -> bool:
    """Execute end-to-end assertions against the provided gateway URL."""
    base_url = base_url.rstrip("/")
    print("=" * 64)
    print(f"🧪 ATLAS Smoke Test — Target: {base_url}")
    print("=" * 64)

    test_origin = "https://atlas-chat.vercel.app"
    headers_common = {
        "Origin": test_origin,
        "ngrok-skip-browser-warning": "true",
    }

    client = httpx.Client(timeout=10.0)

    # 1. CORS Preflight OPTIONS Check
    print("\n[1/3] Verificando Preflight CORS (OPTIONS /health)...")
    try:
        opt_res = client.options(
            f"{base_url}/health",
            headers={
                **headers_common,
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Authorization,Content-Type",
            },
        )
        print(f"   Status: {opt_res.status_code}")
        allow_origin = opt_res.headers.get("access-control-allow-origin")
        print(f"   Access-Control-Allow-Origin: {allow_origin}")

        if opt_res.status_code not in (200, 204):
            print("❌ Falha no Preflight CORS.")
            return False
        if allow_origin not in (test_origin, "*"):
            print(f"❌ Header Access-Control-Allow-Origin inesperado: {allow_origin}")
            return False
        print("   ✅ Preflight CORS validado!")
    except Exception as exc:
        print(f"❌ Erro ao conectar no endpoint: {exc}")
        return False

    # 2. Health Check GET
    print("\n[2/3] Verificando Health Check (GET /health)...")
    try:
        health_res = client.get(f"{base_url}/health", headers=headers_common)
        print(f"   Status: {health_res.status_code}")
        body = health_res.json()
        print(f"   Payload: {body}")
        if health_res.status_code != 200 or body.get("status") != "ok":
            print("❌ Health check retornou payload inválido.")
            return False
        print("   ✅ Gateway operacional e saudável!")
    except Exception as exc:
        print(f"❌ Erro na consulta de health: {exc}")
        return False

    # 3. Server-Sent Events (SSE) Streaming Check
    print("\n[3/3] Verificando Streaming SSE (POST /v1/chat)...")
    chat_headers = {
        **headers_common,
        "Authorization": "Bearer atlas-simulated-token-2026",
        "Content-Type": "application/json",
    }
    chat_payload = {
        "session_id": "smoke-test-s16",
        "message": "Qual é o saldo da conta corrente?",
        "customer_id": "CUST-0001",
    }

    try:
        chunks_received = 0
        with client.stream("POST", f"{base_url}/v1/chat", headers=chat_headers, json=chat_payload) as stream_res:
            print(f"   Status: {stream_res.status_code}")
            content_type = stream_res.headers.get("content-type", "")
            print(f"   Content-Type: {content_type}")

            if stream_res.status_code != 200:
                print(f"❌ Falha na rota de chat. Status: {stream_res.status_code}")
                return False

            if "text/event-stream" not in content_type:
                print(f"❌ Content-Type incorreto para SSE: {content_type}")
                return False

            for line in stream_res.iter_lines():
                if line.strip():
                    chunks_received += 1
                    if chunks_received <= 3:
                        print(f"   [SSE Chunk #{chunks_received}]: {line[:80]}...")

        if chunks_received == 0:
            print("❌ Nenhum evento SSE recebido do stream.")
            return False

        print(f"   ✅ Stream SSE íntegro! Total de blocos recebidos: {chunks_received}")
    except Exception as exc:
        print(f"❌ Erro durante o streaming SSE: {exc}")
        return False

    print("\n" + "=" * 64)
    print("🎉 TODOS OS TESTES DE SMOKE PASSARAM COM SUCESSO!")
    print("=" * 64)
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Smoke test for ATLAS ngrok tunnel")
    parser.add_argument(
        "--url",
        type=str,
        default=None,
        help="Target base URL (default: queries ngrok API or uses http://localhost:8000)",
    )
    args = parser.parse_args()

    target_url = args.url
    if not target_url:
        target_url = get_active_ngrok_url() or "http://localhost:8000"

    success = run_smoke_test(target_url)
    sys.exit(0 if success else 1)
