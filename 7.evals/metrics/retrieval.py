"""Information Retrieval evaluation metrics (Recall@k, Precision@k, MRR) (S17)."""

import re
from typing import Sequence


def _normalize(text: str) -> str:
    """Normalize text for invariant token matching."""
    return re.sub(r"\s+", " ", text.lower().strip())


def calculate_context_recall(
    retrieved_contexts: Sequence[str],
    gold_evidences: Sequence[str],
) -> float:
    """Calculate Context Recall@k.

    Formula:
        Recall@k = (Count of gold evidence chunks retrieved in top k) / (Total gold evidence chunks)
    """
    if not gold_evidences:
        return 1.0
    if not retrieved_contexts:
        return 0.0

    retrieved_norm = [_normalize(c) for c in retrieved_contexts]
    hits = 0

    for gold in gold_evidences:
        gold_norm = _normalize(gold)
        # Check if gold string appears in any retrieved chunk
        if any(gold_norm in chunk or chunk in gold_norm for chunk in retrieved_norm):
            hits += 1

    return round(hits / len(gold_evidences), 4)


def calculate_context_precision(
    retrieved_contexts: Sequence[str],
    gold_evidences: Sequence[str],
) -> float:
    """Calculate Context Precision@k.

    Formula:
        Precision@k = (Relevant chunks among top k) / (k total retrieved chunks)
    """
    if not retrieved_contexts:
        return 0.0
    if not gold_evidences:
        return 0.0

    gold_norms = [_normalize(g) for g in gold_evidences]
    relevant_count = 0

    for chunk in retrieved_contexts:
        chunk_norm = _normalize(chunk)
        if any(gold in chunk_norm or chunk_norm in gold for gold in gold_norms):
            relevant_count += 1

    return round(relevant_count / len(retrieved_contexts), 4)


def calculate_mrr(
    retrieved_contexts: Sequence[str],
    gold_evidences: Sequence[str],
) -> float:
    """Calculate Mean Reciprocal Rank (MRR) for the first relevant evidence hit.

    Formula:
        MRR = 1 / rank_of_first_relevant_chunk (or 0.0 if not found)
    """
    if not retrieved_contexts or not gold_evidences:
        return 0.0

    gold_norms = [_normalize(g) for g in gold_evidences]

    for rank, chunk in enumerate(retrieved_contexts, start=1):
        chunk_norm = _normalize(chunk)
        if any(gold in chunk_norm or chunk_norm in gold for gold in gold_norms):
            return round(1.0 / rank, 4)

    return 0.0
