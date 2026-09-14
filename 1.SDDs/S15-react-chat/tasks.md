# Tasks — S15 · React Chat

- [ ] Initialize React + TypeScript application with Vite under `3.frontend/`.
- [ ] Implement API client, simulated auth header injection, and SSE stream parser in `src/api/sse.ts`.
- [ ] Build core chat components (`ChatContainer`, `MessageList`, `MessageItem`, `ChatInput`) with markdown rendering and auto-scroll.
- [ ] Implement citation badges and slide-out `SourceDrawer` displaying Central Bank provenance metadata.
- [ ] Implement financial simulation widgets (`LoanCard`, `InsuranceCard`, `ConsortiumCard`) with mandatory non-binding disclaimers.
- [ ] Implement `ActionConfirmCard` with explicit user confirmation and cancellation action buttons.
- [ ] Implement `ToolStatusBar` displaying high-level tool execution state without leaking secrets.
- [ ] Implement session management (`useSession`) correlating conversations with `session_id`.
- [ ] Add unit and component tests with Vitest and React Testing Library in `3.frontend/src/__tests__/`.
- [ ] Add E2E smoke test verifying conversational streaming, citation drawers, and action confirmation flow.

## Definition of Done

- All tasks above are complete and merged.
- React Chat application builds cleanly without TypeScript or lint warnings.
- Real-time streaming renders incrementally from the FastAPI Gateway.
- Citation chips open the drawer with source metadata.
- Simulation cards and action confirmation cards render properly and trigger appropriate API calls.
- Automated tests pass in CI.
