"""Evidence-grounded response synthesis adhering to Constitution Principle 4 (S07)."""

import logging

from providers.base import LLMProvider
from providers.config import OllamaSettings
from providers.ollama import OllamaProvider
from rag.retrieval.models import SearchResult

logger = logging.getLogger(__name__)

STANDARD_REFUSAL_MESSAGE = (
    "Não foram encontradas informações suficientes na documentação pública regulatória "
    "do Banco Central para responder com precisão a esta pergunta."
)

SYNTHESIZER_SYSTEM_PROMPT = (
    """Você é o Assistente Especialista Regulatório do BACEN no ATLAS.
Sua missão é responder gerentes bancários com fidelidade factual ABSOLUTA.

DIRETRIZES FUNDAMENTAIS (Princípio 4 da Constituição: Evidência antes de afirmações):
1. Utilize EXCLUSIVAMENTE informações dos trechos de documentos fornecidos em <contexto>.
2. É PROIBIDO inventar regras, prazos, taxas, penalidades ou inferir suposições não documentadas.
3. Se o <contexto> não contiver a resposta exata, responda EXATAMENTE:
   "Não foram encontradas informações suficientes na documentação pública regulatória """
    """do Banco Central para responder com precisão a esta pergunta."
4. Ao citar uma norma, insira o identificador no formato [^ID] (exemplo: [^chunk_id]).
5. Se houver divergência, dê preferência expressa à norma com a data mais recente.
6. Responda em português claro, profissional e objetivo."""
)


def build_context_block(chunks: list[SearchResult]) -> str:
    """Format candidate search chunks into structured XML context."""
    if not chunks:
        return "<contexto>\nNenhum documento disponível.\n</contexto>"

    lines = ["<contexto>"]
    for i, c in enumerate(chunks, 1):
        norm_ref = f" | Norma: {c.metadata.norm_number}" if c.metadata.norm_number else ""
        sec_ref = f" | Seção: {c.metadata.section_title}" if c.metadata.section_title else ""
        date_ref = f" | Data: {c.metadata.publication_date}" if c.metadata.publication_date else ""

        lines.append(f"[Trecho {i} - ID: {c.chunk_id}]")
        lines.append(f"Título: {c.metadata.title}{norm_ref}{sec_ref}{date_ref}")
        lines.append(f"Conteúdo: {c.text.strip()}")
        lines.append("")
    lines.append("</contexto>")
    return "\n".join(lines)


class GroundedSynthesizer:
    """Synthesizes responses grounded exclusively on regulatory context excerpts."""

    def __init__(self, llm_provider: LLMProvider | None = None) -> None:
        """Initialize the synthesizer.

        Args:
            llm_provider: Concrete LLMProvider (defaults to local OllamaProvider).
        """
        self.llm_provider: LLMProvider = (
            llm_provider if llm_provider is not None else OllamaProvider(OllamaSettings())
        )

    async def synthesize(
        self,
        query: str,
        chunks: list[SearchResult],
    ) -> tuple[str, bool]:
        """Synthesize answer from retrieved chunks.

        Args:
            query: User's question.
            chunks: Retrieved and verified regulatory context chunks.

        Returns:
            Tuple of (answer_text, has_sufficient_evidence).
        """
        if not chunks:
            return STANDARD_REFUSAL_MESSAGE, False

        context_block = build_context_block(chunks)
        user_prompt = (
            f'Pergunta do usuário:\n"{query.strip()}"\n\n'
            f"Documentos Regulatórios:\n{context_block}\n\n"
            "Sintetize a resposta fundamentada com citações [^ID] conforme as diretrizes."
        )

        try:
            raw_answer = await self.llm_provider.generate(
                prompt=user_prompt,
                system=SYNTHESIZER_SYSTEM_PROMPT,
            )
            answer = raw_answer.strip()
        except Exception as exc:
            logger.error("LLM synthesis failed: %s", exc, exc_info=True)
            return (
                "Ocorreu uma instabilidade ao sintetizar a resposta com o modelo de linguagem. "
                "Por favor, tente novamente.",
                False,
            )

        # Check if the model explicitly refused due to lack of evidence
        refusal_markers = [
            "não foram encontradas informações suficientes",
            "não há informações suficientes",
            "não consta no contexto",
            "o contexto fornecido não contém",
        ]
        is_refusal = any(marker in answer.lower() for marker in refusal_markers)

        has_sufficient_evidence = not is_refusal
        return answer, has_sufficient_evidence
