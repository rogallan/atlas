# ngrok Integration — ATLAS Banking Copilot

Este diretório contém as configurações e diretrizes para criar um túnel seguro HTTPS com o **ngrok**, expondo o Gateway local FastAPI (`http://localhost:8000`) para a interface Web do ATLAS hospedada na Vercel ou acessada remotamente.

## 1. Pré-requisitos

1. **Instalação do ngrok CLI:**
   - **Windows:** `winget install ngrok.ngrok` ou `choco install ngrok`
   - **macOS:** `brew install ngrok/ngrok/ngrok`
   - **Linux:** `curl -s https://ngrok-agent.s3.amazonaws.com | sudo tar xvz -C /usr/local/bin`

2. **Autenticação:**
   Cadastre-se gratuitamente em [ngrok.com](https://ngrok.com) e configure seu token:
   ```bash
   ngrok config add-authtoken <SEU_TOKEN_AQUI>
   # ou via variável de ambiente:
   export NGROK_AUTHTOKEN="<SEU_TOKEN_AQUI>"
   ```

## 2. Inicialização

Para iniciar o túnel usando o arquivo de configuração deste diretório:

```bash
ngrok start --config 5.infra/ngrok/ngrok.yml atlas-api
```

Ou use o script de automação do projeto:

```bash
uv run python 6.ops/start_tunnel.py
```

## 3. Painel de Inspeção

Enquanto o ngrok estiver em execução, o painel de inspeção de requisições estará disponível localmente em:
👉 **http://localhost:4040**

Lá você pode auditar preflight CORS (`OPTIONS`), headers e latência de cada evento SSE.
