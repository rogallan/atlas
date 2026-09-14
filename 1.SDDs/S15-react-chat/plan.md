# Plan — S15 · React Chat

## 1. Approach

Build the React Chat frontend under `3.frontend/` using Vite, React 18+, TypeScript, and clean modular CSS (or Tailwind if standard in repo, adhering to rich, responsive bank copilot aesthetics). The client acts as a lightweight consumer of the FastAPI Gateway (S03) through ngrok (S16) or local origin, emphasizing streaming responsiveness, citation verification drawers, structured simulation widgets, and HITL action confirmation cards.

## 2. Architecture & Components

```
3.frontend/
├── public/
├── src/
│   ├── api/
│   │   ├── client.ts         # Gateway client, fetch with auth headers
│   │   └── sse.ts            # Server-Sent Events stream reader
│   ├── components/
│   │   ├── chat/
│   │   │   ├── ChatContainer.tsx
│   │   │   ├── MessageList.tsx
│   │   │   ├── MessageItem.tsx
│   │   │   └── ChatInput.tsx
│   │   ├── cards/
│   │   │   ├── LoanCard.tsx          # Simulation widget for S09
│   │   │   ├── InsuranceCard.tsx     # Simulation widget for S10
│   │   │   ├── ConsortiumCard.tsx    # Simulation widget for S11
│   │   │   └── ActionConfirmCard.tsx # HITL confirmation button for S13
│   │   ├── citations/
│   │   │   ├── CitationBadge.tsx
│   │   │   └── SourceDrawer.tsx
│   │   ├── status/
│   │   │   └── ToolStatusBar.tsx     # Controlled transparency indicator
│   │   └── common/
│   │       ├── Header.tsx
│   │       └── ErrorBanner.tsx
│   ├── hooks/
│   │   ├── useChat.ts        # Manages conversation state, streaming buffer, sessions
│   │   └── useSession.ts     # Correlates session_id with backend
│   ├── types/
│   │   └── api.ts            # TypeScript interfaces matching Gateway OpenAPI specs
│   ├── App.tsx
│   └── main.tsx
├── package.json
└── vite.config.ts
```

### Data & Event Flow:
1. **Session Creation:** On mount, `useSession` calls `POST /v1/sessions` to obtain a session UUID (persisted in `sessionStorage`).
2. **User Submission:** `useChat` fires `POST /v1/chat` with message and session ID.
3. **SSE Ingestion:** `sse.ts` parses incoming stream events:
   - `event: tool_start` -> displays "Consultando dados..." badge in `ToolStatusBar`.
   - `event: chunk` -> appends streamed token to current assistant message buffer.
   - `event: citation` -> appends clickable reference to `CitationBadge`.
   - `event: structured_card` -> embeds loan/insurance/consortium card or action proposal.
   - `event: done` -> finalizes stream rendering.
4. **HITL Action:** When an `ActionConfirmCard` is received, user clicks "Confirmar" -> frontend dispatches confirmation payload to `/v1/chat`.

## 3. Key Interfaces & Data Contracts

```typescript
export interface Citation {
  chunk_id: string;
  source_title: string;
  norm_reference?: string;
  section_title?: string;
  source_url_or_path: string;
  excerpt: string;
}

export interface SimulationPayload {
  type: 'loan' | 'insurance' | 'consortium';
  data: Record<string, any>;
  disclaimer: string;
}

export interface ActionConfirmationPayload {
  confirmation_token: string;
  customer_id: string;
  category: string;
  title: string;
  description: string;
  summary_for_human: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant' | 'system';
  content: string;
  citations?: Citation[];
  simulation?: SimulationPayload;
  action_proposal?: ActionConfirmationPayload;
  timestamp: string;
  is_streaming?: boolean;
}
```

## 4. UI/UX Design & Guardrail Principles

- **Rich Aesthetics:** Modern dark/light banking theme with subtle gradients, clear typography, and clean contrast for financial figures.
- **Visual Grounding:** Inline citation tags (e.g. `[BACEN Res. 3.919]`) highlighted with subtle blue badges. Clicking opens `SourceDrawer` with complete citation excerpts.
- **Action Confirmation Card (HITL):** Highlighted with warning amber border, explicitly summarizing the proposed operation and showing two distinctive buttons:
  - `[✓ Confirmar Ação]` (primary button)
  - `[✕ Cancelar]` (secondary outlined button)
- **Controlled Transparency:** Shows high-level operations (e.g. "Simulando empréstimo...") without displaying system prompts, API keys, or raw SQL/MCP payloads.

## 5. Test Strategy

- **Component Unit Tests:** Using Vitest + React Testing Library:
  - `MessageList.test.tsx`: Render text chunks, code blocks, and markdown.
  - `ActionConfirmCard.test.tsx`: Verify clicking "Confirmar" triggers callback with `confirmation_token` and `approved=true`.
  - `CitationDrawer.test.tsx`: Verify badge click opens drawer displaying metadata.
- **Streaming Mock Tests:** Test SSE stream parser handling partial packets, connection drops, and reconnects.
- **E2E Smoke Tests:** Playwright or Cypress tests validating session initialization, prompt submission, stream arrival, and card rendering.

## 6. Risks & Mitigations

- **Risk:** Dropped SSE connections over ngrok tunnel.
  - **Mitigation:** Implement reconnection logic with exponential backoff and visually notify the user with a discreet reconnecting badge.
- **Risk:** Markdown rendering injection (XSS).
  - **Mitigation:** Use sanitized markdown renderer (e.g. `react-markdown` with `rehype-sanitize`) preventing script tag execution.
