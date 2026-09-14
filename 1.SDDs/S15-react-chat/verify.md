# Verify — S15 · React Chat

## Evidence checklist

- [ ] Video or test log demonstrating real-time SSE streaming text arrival without UI stutter.
- [ ] UI interaction test proving that clicking a citation badge opens the `SourceDrawer` displaying Central Bank norm title, article, and excerpt.
- [ ] Visual inspection and test output showing rendered cards for loan, insurance, and consortium simulations with mandatory non-binding disclaimers.
- [ ] Human-in-the-Loop test log confirming that clicking "Confirmar Ação" sends the user approval event to `/v1/chat`, while "Cancelar" aborts the operation.
- [ ] Test log demonstrating graceful display of network error banner when backend or ngrok tunnel is unreachable.

## Sign-off

- [ ] Reviewed against `spec.md` — all requirements (R1–R6) satisfied.
- [ ] Reviewed against `plan.md` — component tree, SSE event handlers, and card contracts match implementation.
- [ ] No task in `tasks.md` is checked without corresponding evidence above.
