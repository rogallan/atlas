"""Automation script to launch ngrok tunnel and extract public HTTPS URL (S16)."""

import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import httpx

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Dynamically locate repository root regardless of current working directory
_curr = Path(__file__).resolve().parent
REPO_ROOT = _curr
while REPO_ROOT.parent != REPO_ROOT:
    if (REPO_ROOT / "pyproject.toml").exists() or (REPO_ROOT / ".git").exists():
        break
    REPO_ROOT = REPO_ROOT.parent

# Load .env if present
_env_path = REPO_ROOT / ".env"
if _env_path.exists():
    for line in _env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip("'\""))

LOCAL_API_URL = "http://localhost:8000/health"
NGROK_API_URL = "http://127.0.0.1:4040/api/tunnels"

# Check possible config file locations relative to repo root
_cfg_5infra = REPO_ROOT / "5.infra" / "ngrok" / "ngrok.yml"
_cfg_infra = REPO_ROOT / "infra" / "ngrok" / "ngrok.yml"
CONFIG_PATH = _cfg_5infra if _cfg_5infra.exists() else _cfg_infra


def check_local_gateway() -> bool:
    """Verify if the FastAPI Gateway is running locally on port 8000."""
    try:
        response = httpx.get(LOCAL_API_URL, timeout=2.0)
        return response.status_code == 200
    except Exception:
        return False


def get_public_url() -> str | None:
    """Query ngrok local inspection API on port 4040 to extract public HTTPS endpoint."""
    try:
        response = httpx.get(NGROK_API_URL, timeout=1.5)
        if response.status_code == 200:
            data: dict[str, Any] = response.json()
            tunnels = data.get("tunnels", [])
            for tunnel in tunnels:
                public_url: str = tunnel.get("public_url", "")
                if public_url.startswith("https://"):
                    return public_url
            if tunnels:
                return tunnels[0].get("public_url")
    except Exception:
        pass
    return None


def print_banner(url: str) -> None:
    print("\n" + "=" * 64)
    print("🚀 ATLAS ngrok tunnel ativo com sucesso!")
    print(f"🌐 Public HTTPS URL: {url}")
    print(f"⚙️  Configure no Vercel: NEXT_PUBLIC_API_BASE_URL={url}")
    print("📊 Painel de Inspeção: http://localhost:4040")
    print("=" * 64 + "\n")


def start_tunnel() -> None:
    """Launch ngrok and wait for public HTTPS endpoint resolution."""
    print("=" * 64)
    print("🌐 ATLAS Banking Copilot — ngrok Tunnel Manager")
    print("=" * 64)

    # 1. Health check local gateway
    if not check_local_gateway():
        print("⚠️  Aviso: O Gateway FastAPI não respondeu em http://localhost:8000/health.")
        print("💡 Inicie o servidor em outro terminal: uv run uvicorn api.main:app --port 8000\n")

    # 2. Check if tunnel is already running on port 4040
    existing_url = get_public_url()
    if existing_url:
        print("✅ Túnel ngrok já em execução detectado!")
        print_banner(existing_url)
        return

    # 3. Launch ngrok subprocess
    authtoken = os.getenv("NGROK_AUTHTOKEN")
    cmd = ["ngrok", "http", "8000"]
    if CONFIG_PATH.exists():
        cmd = ["ngrok", "start", "--config", str(CONFIG_PATH), "atlas-api"]

    if authtoken:
        cmd.extend(["--authtoken", authtoken])

    cmd_display = cmd[:-2] + ["--authtoken", "***"] if authtoken else cmd
    print(f"🚀 Iniciando processo ngrok: {' '.join(cmd_display)}...")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(REPO_ROOT),
            env=os.environ.copy(),
        )
    except FileNotFoundError:
        print("❌ Erro: Executável 'ngrok' não encontrado no PATH do sistema.")
        print(
            "Instale o ngrok via: winget install ngrok.ngrok (Windows) "
            "ou brew install ngrok (macOS)"
        )
        sys.exit(1)

    # 4. Poll ngrok local API with early exit on process crash
    print("⏳ Aguardando atribuição de URL pública...")
    public_url = None
    for _ in range(25):
        time.sleep(0.5)

        # Check if ngrok died unexpectedly
        if proc.poll() is not None:
            _, stderr = proc.communicate()
            print("\n❌ O processo do ngrok encerrou inesperadamente:")
            for line in stderr.splitlines():
                if "ERROR:" in line or "ERR_NGROK" in line or "authentication" in line.lower():
                    print(f"   {line.strip()}")
            if "ERR_NGROK_4018" in stderr or "not authenticated" in stderr.lower():
                print("\n🔑 Ação Necessária: Autenticação do ngrok pendente.")
                print("1. Acesse: https://dashboard.ngrok.com/get-started/your-authtoken")
                print("2. Execute no terminal: ngrok config add-authtoken <SEU_TOKEN>")
                print("   (ou defina a variável: $env:NGROK_AUTHTOKEN = '<SEU_TOKEN>')")
            sys.exit(1)

        public_url = get_public_url()
        if public_url:
            break

    if not public_url:
        print("❌ Falha ao obter URL pública do ngrok após 12 segundos.")
        print(
            "Verifique se seu NGROK_AUTHTOKEN foi configurado: ngrok config add-authtoken <TOKEN>"
        )
        proc.terminate()
        sys.exit(1)

    print_banner(public_url)

    try:
        print("Pressione CTRL+C para encerrar o túnel.")
        proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando túnel ngrok...")
        proc.terminate()
        proc.wait()
        print("✅ Túnel encerrado com sucesso.")


if __name__ == "__main__":
    start_tunnel()
