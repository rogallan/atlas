# Runbook Operacional — Túnel ngrok (S16)

> **Serviço:** Integração Externa FastAPI <-> Vercel via ngrok  
> **Classificação:** Operações / Infraestrutura Local  
> **Objetivo:** Expor com segurança o Gateway local FastAPI (`:8000`) para o frontend React hospedado na Vercel sem expor portas de roteador ou hospedar dados em nuvem pública (princípio *Local-first*).

---

## 1. Visão Geral da Arquitetura

```
[ Usuário / Navegador ]
           │
           ▼
[ Frontend Vercel (Next.js) ] 
           │  (HTTPS público)
           ▼
[ ngrok Cloud Edge (*.ngrok-free.app) ]
           │  (Túnel TLS Criptografado)
           ▼
[ ngrok Client Local (:4040) ]
           │  (Forward HTTP)
           ▼
[ FastAPI Gateway Local (:8000) ]
   ├── LangGraph Orchestrator
   ├── Ollama Local (:11434)
   ├── ChromaDB Vector Store
   └── Servidores MCP (Clientes, Crédito, Seguros, Consórcio, Tarifas, Chamados)
```

---

## 2. Pré-requisitos

1. **Conta e Token ngrok:**
   - Obtenha gratuitamente em: [dashboard.ngrok.com](https://dashboard.ngrok.com)
   - Obtenha seu Authtoken no painel do ngrok.
2. **ngrok CLI instalado:**
   - Windows: `winget install ngrok.ngrok`
   - macOS: `brew install ngrok`
   - Linux: `curl -s https://ngrok-agent.s3.amazonaws.com | sudo tar xvz -C /usr/local/bin`
3. **Python & Ambiente Virtual:**
   - `uv` instalado e ambiente ativo no repositório `atlas`.

---

## 3. Passo a Passo de Execução

### Passo 1: Iniciar o Backend Local
Em um terminal dedicado na raiz do projeto:
```powershell
uv run uvicorn api.main:app --port 8000
```
Verifique se a saúde responde em: `http://localhost:8000/health`.

### Passo 2: Configurar o Authtoken do ngrok (apenas na 1ª vez)
```powershell
ngrok config add-authtoken SEU_TOKEN_AQUI
```
*Ou exporte a variável de ambiente `NGROK_AUTHTOKEN`.*

### Passo 3: Iniciar o Túnel ngrok
Execute o script automatizado do ATLAS:
```powershell
uv run python 6.ops/start_tunnel.py
```
O script iniciará o processo, consultará a API interna do ngrok (`http://127.0.0.1:4040`) e exibirá o banner com o endereço público:
```
================================================================
🚀 ATLAS ngrok tunnel ativo com sucesso!
🌐 Public HTTPS URL: https://b412-177-136-22-10.ngrok-free.app
⚙️  Configure no Vercel: NEXT_PUBLIC_API_BASE_URL=https://b412-177-136-22-10.ngrok-free.app
📊 Painel de Inspeção: http://localhost:4040
================================================================
```

### Passo 4: Sincronizar Variáveis de Ambiente na Vercel
1. Acesse o projeto na **Vercel** > **Settings** > **Environment Variables**.
2. Atualize ou adicione:
   - `NEXT_PUBLIC_API_BASE_URL`: `<URL_PUBLICA_DO_NGROK>`
3. Dispare um novo deploy ou use a URL diretamente para testes de preview.

### Passo 5: Executar o Teste de Fumaça (Smoke Test)
Em outro terminal, valide preflight CORS, saúde do Gateway e integridade do streaming SSE:
```powershell
uv run python 6.ops/smoke_test_tunnel.py
```
O teste valida automaticamente:
1. `OPTIONS /health` com origem `https://atlas-chat.vercel.app` e headers CORS.
2. `GET /health` retornando status `ok`.
3. `POST /v1/chat` com recepção não-bufferizada de Server-Sent Events (`text/event-stream`).

---

## 4. Monitoramento e Inspeção de Tráfego

Com o túnel ativo, abra no navegador:
👉 **http://localhost:4040**

O painel local do ngrok permite:
- Visualizar todas as requisições HTTP em tempo real.
- Analisar headers de Preflight `OPTIONS` e status de resposta.
- Reexecutar (*replay*) requisições com 1 clique para depuração.

---

## 5. Resolução de Problemas (Troubleshooting)

### Erro 1: Tela de aviso intermediária do ngrok ("You are about to visit...")
- **Causa:** No plano gratuito do ngrok, requisições de navegador podem receber uma página HTML de confirmação intermediária.
- **Solução:** O frontend do ATLAS já inclui o header obrigatório:
  `ngrok-skip-browser-warning: true` em todas as requisições HTTP/SSE.

### Erro 2: `CORS Policy: No 'Access-Control-Allow-Origin' header is present`
- **Causa:** O domínio da Vercel não foi reconhecido pelo middleware CORS.
- **Solução:** O middleware `2.src/api/middleware/cors.py` autoriza por padrão `https://atlas-chat.vercel.app` e domínios de preview `https://.*\.vercel\.app`. Para domínios customizados, defina:
  ```powershell
  $env:ATLAS_ALLOWED_ORIGINS="https://meu-dominio-customizado.com"
  ```

### Erro 3: Streaming SSE travando ou entregando texto de uma vez só
- **Causa:** Camadas intermediárias de proxy bufferizando a resposta HTTP.
- **Solução:** O FastAPI Gateway emite `X-Accel-Buffering: no` e `Cache-Control: no-cache` nas respostas de `/v1/chat`.
