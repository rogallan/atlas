"""Groundedness and Hallucination Detection metrics for GenAI synthesis (S17)."""

import re
from collections.abc import Sequence


def _split_into_claims(text: str) -> list[str]:
    """Segment an answer text into candidate factual proposition statements."""
    # Split on sentence terminals followed by space, avoiding splitting decimals (e.g., 1.000)
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n+", text)
    claims: list[str] = []
    for s in raw_sentences:
        cleaned = s.strip()
        # Keep non-empty statements with at least 3 words
        if len(cleaned.split()) >= 3:
            claims.append(cleaned)
    return claims


def calculate_groundedness_score(
    answer: str,
    context_chunks: Sequence[str],
) -> tuple[float, list[str]]:
    """Evaluate factual groundedness of the generated answer against context chunks.

    Returns:
        tuple of (groundedness_score: float, ungrounded_claims: list[str])

    Formula:
        Groundedness = (Substantiated Claims) / (Total Claims)
    """
    if not answer or not answer.strip():
        return 0.0, ["Empty answer"]

    if not context_chunks:
        # Without context, any factual assertion is considered ungrounded
        claims = _split_into_claims(answer)
        return (1.0, []) if not claims else (0.0, claims)

    full_context = " ".join(context_chunks).lower()
    claims = _split_into_claims(answer)

    if not claims:
        return 1.0, []

    substantiated = 0
    ungrounded: list[str] = []

    # Stopwords to filter when extracting key tokens
    stopwords = {
        "o",
        "a",
        "os",
        "as",
        "um",
        "uma",
        "uns",
        "umas",
        "de",
        "do",
        "da",
        "dos",
        "das",
        "em",
        "no",
        "na",
        "nos",
        "nas",
        "por",
        "pelo",
        "pela",
        "pelos",
        "pelas",
        "com",
        "para",
        "que",
        "e",
        "ou",
        "se",
        "como",
        "ao",
        "aos",
        "à",
        "às",
        "é",
        "são",
        "foi",
        "foram",
        "ser",
        "estar",
        "está",
        "estão",
        "ter",
        "tem",
        "temos",
        "têm",
    }

    for claim in claims:
        # Extract meaningful alphanumeric tokens (length >= 3 and not stopword)
        tokens = [
            t.lower()
            for t in re.findall(r"\b[A-Za-zÀ-ÿ0-9%R$]+\b", claim)
            if len(t) >= 3 and t.lower() not in stopwords
        ]

        if not tokens:
            substantiated += 1
            continue

        # Check token containment in retrieved context
        token_hits = sum(1 for t in tokens if t in full_context)
        overlap_ratio = token_hits / len(tokens)

        # A claim is supported if >= 60% of its content tokens are grounded in context
        if overlap_ratio >= 0.60:
            substantiated += 1
        else:
            ungrounded.append(claim)

    score = round(substantiated / len(claims), 4)
    return score, ungrounded
