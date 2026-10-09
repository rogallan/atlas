"""Synthesizer Node: Formats grounded answers, simulation cards, and HITL proposals (S14)."""

import logging

from agent.graph.state import AgentState, AgentStep

logger = logging.getLogger("atlas.agent.graph.synthesizer_node")


class SynthesizerNode:
    """Assembles final structured response from tool outputs, citations, and confirmation states."""

    def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("synthesizer_node")
        state.current_step = AgentStep.SYNTHESIZER

        # 1. Action Confirmation Proposal (Phase 1)
        if state.requires_human_confirmation and state.confirmation_payload:
            payload = state.confirmation_payload
            state.final_response = (
                "⚠️ **Ação Requer Autorização do Operador (Human-in-the-Loop)**\n\n"
                f"📋 **{payload.get('summary_for_human')}**\n\n"
                f"- **Cliente:** `{payload.get('customer_id')}`\n"
                f"- **Categoria:** `{payload.get('category')}`\n"
                f"- **Prioridade:** `{payload.get('priority')}`\n"
                f"- **Token de Confirmação:** `{payload.get('confirmation_token')}`\n"
                f"- **Expira em:** `{payload.get('expires_at')}`\n\n"
                "Para confirmar e efetivar a abertura deste chamado no sistema bancário, "
                "clique em **[Confirmar Abertura]** ou envie:\n"
                f"`confirmar {payload.get('confirmation_token')}`\n\n"
                f"Para recusar, envie `cancelar {payload.get('confirmation_token')}`."
            )
            return state

        # 2. RAG Knowledge Responses
        for out in state.tool_outputs:
            if out.get("tool") == "rag_retrieval":
                answer = out.get("answer", "")
                citations_text = ""
                if state.citations:
                    citations_text = "\n\n📚 **Fontes Regulatórias:**\n" + "\n".join(
                        f"- [{c.get('document_title')}, {c.get('section')}] ({c.get('quote')})"
                        for c in state.citations[:3]
                    )
                state.final_response = f"{answer}{citations_text}"
                return state

        # 3. MCP Customer Lookup Responses
        for out in state.tool_outputs:
            if out.get("tool") == "mcp_customer":
                output_type = out.get("type")
                if output_type == "customer_profile":
                    p = out.get("profile", {})
                    state.final_response = (
                        f"👤 **Perfil do Cliente: {p.get('name')}**\n\n"
                        f"- **ID:** `{p.get('customer_id')}`\n"
                        f"- **CPF:** `{p.get('cpf_masked')}`\n"
                        f"- **Segmento:** `{p.get('segment', '').upper()}`\n"
                        f"- **Renda Mensal:** R$ {p.get('monthly_income', 0):,.2f}\n"
                        f"- **Perfil de Risco:** `{p.get('risk_profile')}`"
                    )
                elif output_type == "account_balance_and_history":
                    accs = out.get("accounts", [])
                    total_bal = sum(a.get("balance", 0.0) for a in accs)
                    lines = [f"💳 **Contas do Cliente ({len(accs)} conta(s)):**\n"]
                    for a in accs:
                        acc_type = str(a.get("account_type", "")).title()
                        curr = a.get("currency", "BRL")
                        bal_val = a.get("balance", 0.0)
                        lines.append(f"- **{acc_type}:** {curr} {bal_val:,.2f}")
                    lines.append(f"\n- **Saldo Consolidado:** R$ {total_bal:,.2f}")
                    state.final_response = "\n".join(lines)
                else:
                    cnt = len(out.get("products", []))
                    state.final_response = (
                        f"📦 **Produtos do Cliente:** {cnt} contrato(s) ativo(s)."
                    )
                return state

        # 4. MCP Simulation Responses
        for out in state.tool_outputs:
            if out.get("tool") == "mcp_loan":
                sim = out.get("simulation", {})
                monthly_rate = sim.get("interest_rate_monthly", 0) * 100
                cet_annual = sim.get("cet_annual", 0) * 100
                state.final_response = (
                    "📊 **Simulação de Crédito (Valores Estimados)**\n\n"
                    f"- **Modalidade:** `{sim.get('product_type')}`\n"
                    f"- **Valor Solicitado:** R$ {sim.get('requested_amount', 0):,.2f}\n"
                    f"- **Parcela Mensal:** R$ {sim.get('monthly_installment', 0):,.2f}\n"
                    f"- **IOF Total:** R$ {sim.get('total_iof', 0):,.2f}\n"
                    f"- **Taxa de Juros Mensal:** {monthly_rate:.2f}%\n"
                    f"- **Custo Efetivo Total (CET Anual):** {cet_annual:.2f}%\n"
                    f"- **Total a Pagar:** R$ {sim.get('total_payable', 0):,.2f}\n\n"
                    "⚠️ *Simulação para fins consultivos. Contratação sujeita a análise de crédito.*"
                )
                return state

            elif out.get("tool") == "mcp_insurance":
                q = out.get("quote", {})
                state.final_response = (
                    "🛡️ **Cotação de Seguro**\n\n"
                    f"- **Produto:** `{q.get('product_type')}`\n"
                    f"- **Cobertura (LMI):** R$ {q.get('coverage_amount', 0):,.2f}\n"
                    f"- **Prêmio Mensal:** R$ {q.get('total_premium_monthly', 0):,.2f} "
                    f"(IOF: R$ {q.get('iof_tax', 0):,.2f})\n"
                    f"- **Tipo de Franquia:** `{q.get('deductible_type')}`"
                )
                return state

            elif out.get("tool") == "mcp_consortium":
                c = out.get("simulation", {})
                admin_fee = c.get("admin_fee_total_pct", 0) * 100
                state.final_response = (
                    "🤝 **Simulação de Consórcio**\n\n"
                    f"- **Categoria:** `{c.get('product_type')}`\n"
                    f"- **Crédito:** R$ {c.get('credit_amount', 0):,.2f}\n"
                    f"- **Prazo:** {c.get('term_months')} meses\n"
                    f"- **Parcela Mensal:** R$ {c.get('total_monthly_installment', 0):,.2f}\n"
                    f"- **Taxa de Administração:** {admin_fee:.1f}% total"
                )
                return state

        # 5. MCP Ticket Committed / Rejected Responses
        for out in state.tool_outputs:
            if out.get("tool") == "mcp_ticket":
                if out.get("type") == "ticket_confirmed":
                    tck = out.get("ticket", {})
                    state.final_response = (
                        "✅ **Chamado Aberto com Sucesso!**\n\n"
                        f"- **Protocolo:** `{tck.get('ticket_id')}`\n"
                        f"- **Status:** `{tck.get('status')}`\n"
                        f"- **Operador:** `{tck.get('operator_id')}`\n"
                        f"- **Data/Hora:** `{tck.get('created_at')}`"
                    )
                elif out.get("type") == "action_rejected":
                    msg = out.get("message", "A criação do chamado foi rejeitada.")
                    state.final_response = f"🚫 **Ação Cancelada pelo Operador**\n\n{msg}"
                return state

        # Default fallback synthesis
        state.final_response = (
            state.final_response or "Processamento concluído com sucesso pelo copiloto bancário."
        )
        return state
