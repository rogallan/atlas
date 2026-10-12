# Tasks — S15 · React Chat

- [x] Initialize React + TypeScript application with Next.js (App Router) under `3.frontend/`.
- [x] Implement API client, simulated auth header injection, and SSE stream parser in `src/hooks/useChat.ts`.
- [x] Build core chat components (`ChatContainer`, `MessageItem`, `ChatInput`) with markdown rendering and auto-scroll.
- [x] Implement clear navigation menus categorized by MCPs (Customer, Loan, Insurance, Consortium, Tariff, Ticket) and synthetic customer database in `src/components/menu/SidebarMenu.tsx`.
- [x] Implement citation badges and slide-out `SourceDrawer` displaying Central Bank provenance metadata.
- [x] Implement financial simulation widgets (`LoanCard`, `InsuranceCard`, `ConsortiumCard`) with mandatory non-binding disclaimers.
- [x] Implement `ActionConfirmCard` with explicit user confirmation and cancellation action buttons (HITL).
- [x] Implement `ToolStatusBar` displaying high-level tool execution state without leaking secrets.
- [x] Implement session management (`useChat`) correlating conversations with `session_id`.
- [x] Validate production build with Next.js compiler (`next build`) generating static pages without errors.

## Definition of Done

- [x] All tasks above are complete and merged.
- [x] React Chat application builds cleanly without TypeScript or lint warnings (`next build` passed).
- [x] Real-time streaming renders incrementally from the FastAPI Gateway.
- [x] Citation chips open the drawer with source metadata.
- [x] Simulation cards and action confirmation cards render properly and trigger appropriate API calls.
- [x] Structured MCP navigation menus provide instant query injection with synthetic customer context.
