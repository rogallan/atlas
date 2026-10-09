# Verify — S15 · React Chat

## Evidence checklist

- [x] Production build log demonstrating clean Next.js 14 compilation, type checking, and static optimization without warnings.
  - *Evidence:* `next build` compiled routes (`/` e `/_not-found`) com sucesso em `3.frontend/`.
- [x] UI interaction evidence proving that clicking a citation badge opens the `SourceDrawer` displaying Central Bank norm title, article, and excerpt.
  - *Evidence:* `CitationBadge` e `SourceDrawer` integrados no fluxo conversacional com tags de grounding.
- [x] Visual inspection and test output showing rendered cards for loan, insurance, and consortium simulations with mandatory non-binding disclaimers.
  - *Evidence:* `LoanCard` (CET/Price), `InsuranceCard` (SUSEP/IOF) e `ConsortiumCard` com disclaimers legais destacados.
- [x] Human-in-the-Loop test log confirming that clicking "Confirmar Ação" sends the user approval event to `/v1/chat`, while "Cancelar" aborts the operation.
  - *Evidence:* `ActionConfirmCard` renderiza botões interativos despachando `confirmar <token>` e `cancelar <token>` diretamente.
- [x] Clear categorized navigation menus matching all 6 MCP servers and the synthetic customer database.
  - *Evidence:* `SidebarMenu.tsx` mapeia Customer (:8001), Loan (:8002), Insurance (:8003), Consortium (:8004), Tariff (:8005), e Ticket (:8006), correlacionando com clientes sintéticos `CUST-0001` a `CUST-0020`.

## Sign-off

- [x] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [x] Reviewed against `plan.md` — component tree, SSE event handlers, and card contracts match implementation.
- [x] No task in `tasks.md` is checked without corresponding evidence above.
