# S00 — Constitution + arquitetura · Plano técnico

## 1. Abordagem

Este item não produz código; produz dois artefatos de decisão que servem de
referência para todo o resto do projeto. O plano é redigir, revisar e versionar
ambos os documentos em uma única iteração curta, antes de iniciar S01.

## 2. Estrutura de `constitution.md`

```
constitution.md
├── Propósito do documento
├── Princípios (local-first, segurança por padrão, ferramentas explícitas,
│                evidência antes de afirmação, testes antes de release,
│                dados fictícios sempre)
├── Como usar este documento (todo spec.md deve referenciá-lo quando relevante)
└── Processo de mudança (como um princípio pode ser revisto — via ADR)
```

## 3. Estrutura de `architecture.md`

```
architecture.md
├── Visão geral (diagrama textual do fluxo: usuário → Front → API → Agent →
│                 RAG/MCP → resposta)
├── Front (React Chat)        — responsabilidade, o que NÃO faz
├── API (FastAPI)             — fronteira do produto, contratos, streaming
├── Agent                     — Router → Knowledge/RAG ou Query/Action → Validation
├── MCP                       — capacidades de negócio desacopladas
├── Knowledge/RAG             — ingestão → chunking → embeddings → retrieval
├── Infra                     — local (Docker+Ollama+Vector+MCP) e cloud (Terraform/AWS)
└── Contratos entre módulos   — o que cada fronteira aceita/retorna, e o que
                                 nunca deve atravessar essa fronteira (ex: dados
                                 crus de cliente não devem ir direto ao Front)
```

O diagrama textual do fluxo principal:

```
Usuário → React Chat (Front)
        → FastAPI (API: auth simulada, sessão, streaming)
        → Agent Router
             ├─ Knowledge → RAG (retrieval + citação)
             └─ Query/Action → MCP (perfil, empréstimo, seguro, consórcio, tarifas, ticket)
        → Validation/Critic (grounding, schema, política)
        → Resposta (streaming, com fontes/citações quando aplicável)
```

## 4. Decisões já tomadas no PDI (herdadas, não reabertas aqui)

- LLM local via Ollama (S04 detalha o adapter).
- Front publicado na Vercel, backend local exposto via ngrok (S16 detalha).
- Terraform representa alternativa AWS, não é dependência do dia a dia (S21).
- Multiagente só onde houver benefício mensurável — arquitetura parte de agente
  único com Router, evoluindo apenas se justificado por evidência (evals).

## 5. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Princípios ficarem genéricos demais e não guiarem decisões reais | Cada princípio deve ter pelo menos um exemplo concreto de aplicação no ATLAS |
| Arquitetura documentada divergir do código com o tempo | `architecture.md` é revisado a cada trimestre (checkpoint no início de T2, T3, T4) |
| Escopo do documento crescer para incluir detalhes de implementação | Detalhes de implementação ficam nos specs de cada Sxx; este documento é só fronteiras e contratos |

## 6. Saída esperada

Dois arquivos Markdown versionados na raiz do repositório (`constitution.md`,
`architecture.md`), referenciados a partir do `README.md` do projeto.
