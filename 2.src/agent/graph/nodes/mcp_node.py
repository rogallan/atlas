"""MCP Tool Node: Dispatches requests to specialized MCP banking domain servers (S14)."""

import logging
import re

from agent.graph.state import AgentState, AgentStep
from agent.router.models import IntentType
from mcp.consortium.models import ConsortiumSegment
from mcp.consortium.tools import ConsortiumTools
from mcp.customer.tools import CustomerTools
from mcp.insurance.tools import InsuranceTools
from mcp.loan.models import LoanModality
from mcp.loan.tools import LoanTools
from mcp.tariff.models import ChannelType
from mcp.tariff.tools import TariffTools
from mcp.ticket.models import ActionRejectedError, TicketCategory, TicketPriority
from mcp.ticket.tools import TicketTools

logger = logging.getLogger("atlas.agent.graph.mcp_node")


class MCPNode:
    """Dispatches requests to S08-S13 MCP servers based on classified intent and entities."""

    def __init__(
        self,
        customer_tools: CustomerTools | None = None,
        loan_tools: LoanTools | None = None,
        insurance_tools: InsuranceTools | None = None,
        consortium_tools: ConsortiumTools | None = None,
        tariff_tools: TariffTools | None = None,
        ticket_tools: TicketTools | None = None,
    ) -> None:
        self.customer_tools = customer_tools or CustomerTools()
        self.loan_tools = loan_tools or LoanTools()
        self.insurance_tools = insurance_tools or InsuranceTools()
        self.consortium_tools = consortium_tools or ConsortiumTools()
        self.tariff_tools = tariff_tools or TariffTools()
        self.ticket_tools = ticket_tools or TicketTools()

    def _extract_customer_id(self, state: AgentState) -> str:
        """Extract customer ID from intent entities or regex fallback."""
        if state.intent_decision and state.intent_decision.entities.customer_id:
            cid = str(state.intent_decision.entities.customer_id).upper()
            parts = cid.split("-")
            if len(parts) == 2 and len(parts[1]) == 3:
                return f"{parts[0]}-0{parts[1]}"
            return cid

        match = re.search(r"\b(CUST-\d{3,4})\b", state.user_message, re.IGNORECASE)
        if match:
            cid = str(match.group(1).upper())
            parts = cid.split("-")
            if len(parts) == 2 and len(parts[1]) == 3:
                return f"{parts[0]}-0{parts[1]}"
            return cid

        return "CUST-0001"  # Default fallback synthetic customer

    def _extract_token(self, text: str) -> str | None:
        """Extract confirmation token if present in user message."""
        match = re.search(r"\b(tkn_[A-Za-z0-9_-]+)\b", text)
        return match.group(1) if match else None

    def _is_confirmation_message(self, text: str) -> tuple[bool, bool]:
        """Check if message represents human confirmation or rejection.

        Returns:
            (is_confirmation_turn, approved)
        """
        low = text.lower()
        if any(w in low for w in ["confirmar", "confirmo", "aprovar", "autorizo", "sim"]):
            return True, True
        if any(w in low for w in ["cancelar", "rejeitar", "recusar", "não", "nao"]):
            return True, False
        return False, False

    def __call__(self, state: AgentState) -> AgentState:
        state.step_count += 1
        state.node_history.append("mcp_node")
        state.current_step = AgentStep.MCP

        intent = state.intent_decision.intent if state.intent_decision else IntentType.QUERY
        customer_id = self._extract_customer_id(state)

        logger.info(
            "MCP node processing intent='%s' for customer='%s' in session '%s'",
            intent.value,
            customer_id,
            state.session_id,
        )

        try:
            if intent == IntentType.QUERY:
                self._handle_customer_query(state, customer_id)
            elif intent == IntentType.SIMULATION:
                self._handle_simulation(state, customer_id)
            elif intent == IntentType.ACTION:
                self._handle_action(state, customer_id)
            else:
                self._handle_customer_query(state, customer_id)

        except Exception as exc:
            logger.exception("Error executing MCP tool in session '%s'", state.session_id)
            state.error_message = f"Erro na execução da ferramenta MCP: {exc}"

        return state

    def _handle_customer_query(self, state: AgentState, customer_id: str) -> None:
        """Handle customer profile, balance, or history lookups."""
        msg_lower = state.user_message.lower()

        if any(k in msg_lower for k in ["saldo", "balance", "conta", "extrato", "transaç"]):
            accounts = self.customer_tools.get_customer_accounts(customer_id)
            history = self.customer_tools.get_financial_history(customer_id, limit=5)
            state.tool_outputs.append(
                {
                    "tool": "mcp_customer",
                    "type": "account_balance_and_history",
                    "accounts": [a.model_dump() for a in accounts],
                    "history": [h.model_dump() for h in history],
                }
            )
        else:
            profile = self.customer_tools.get_customer_profile(customer_id)
            state.tool_outputs.append(
                {
                    "tool": "mcp_customer",
                    "type": "customer_profile",
                    "profile": profile.model_dump(),
                }
            )

    def _handle_simulation(self, state: AgentState, customer_id: str) -> None:
        """Handle loan, insurance, consortium, or tariff simulation."""
        msg_lower = state.user_message.lower()
        entities = state.intent_decision.entities if state.intent_decision else None

        amount = (entities and entities.amount) or 15000.0
        term_months = (entities and entities.term_months) or 24

        if any(k in msg_lower for k in ["seguro", "apólice", "apolice", "vida", "auto"]):
            quote = self.insurance_tools.simulate_insurance_quote(
                product_id="life_standard",
                insured_capital=max(50000.0, amount),
                customer_id=customer_id,
            )
            state.tool_outputs.append(
                {
                    "tool": "mcp_insurance",
                    "type": "insurance_quote",
                    "quote": quote.model_dump(),
                }
            )
        elif any(k in msg_lower for k in ["consórcio", "consorcio", "cota", "lance"]):
            cons_sim = self.consortium_tools.simulate_consortium(
                modality=ConsortiumSegment.AUTOMOTIVE,
                credit_amount=max(30000.0, amount),
                term_months=max(36, term_months),
            )
            state.tool_outputs.append(
                {
                    "tool": "mcp_consortium",
                    "type": "consortium_simulation",
                    "simulation": cons_sim.model_dump(),
                }
            )
        elif any(k in msg_lower for k in ["tarifa", "pacote", "cesta"]):
            fee = self.tariff_tools.get_service_fee(
                service_code="withdrawal",
                channel=ChannelType.BRANCH_COUNTER,
            )
            state.tool_outputs.append(
                {
                    "tool": "mcp_tariff",
                    "type": "tariff_fee",
                    "fee": fee.model_dump(),
                }
            )
        else:
            loan_sim = self.loan_tools.simulate_loan(
                customer_id=customer_id,
                amount=amount,
                term_months=term_months,
                modality=LoanModality.PERSONAL_CREDIT,
            )
            state.tool_outputs.append(
                {
                    "tool": "mcp_loan",
                    "type": "loan_simulation",
                    "simulation": loan_sim.model_dump(),
                }
            )

    def _handle_action(self, state: AgentState, customer_id: str) -> None:
        """Handle state-changing ticket actions with Human-in-the-Loop two-phase commit."""
        token = self._extract_token(state.user_message)
        is_confirm, approved = self._is_confirmation_message(state.user_message)

        # Check if this turn is an explicit Phase 2 confirmation
        if token and is_confirm:
            try:
                ticket = self.ticket_tools.confirm_and_create_ticket(
                    confirmation_token=token,
                    approved_by_user=approved,
                    operator_id=state.operator_id,
                )
                state.requires_human_confirmation = False
                state.tool_outputs.append(
                    {
                        "tool": "mcp_ticket",
                        "type": "ticket_confirmed",
                        "ticket": ticket.model_dump(),
                    }
                )
            except ActionRejectedError as exc:
                state.requires_human_confirmation = False
                state.tool_outputs.append(
                    {
                        "tool": "mcp_ticket",
                        "type": "action_rejected",
                        "message": exc.message,
                    }
                )
            return

        # Otherwise, Phase 1: Prepare draft and require human confirmation
        draft = self.ticket_tools.prepare_ticket(
            customer_id=customer_id,
            category=TicketCategory.CONTESTATION,
            title="Solicitação de atendimento operacional",
            description=state.user_message,
            priority=TicketPriority.MEDIUM,
            operator_id=state.operator_id,
        )

        state.requires_human_confirmation = True
        state.confirmation_payload = draft.model_dump()
        state.tool_outputs.append(
            {
                "tool": "mcp_ticket",
                "type": "ticket_draft_prepared",
                "draft": draft.model_dump(),
            }
        )
