"""Citation extraction, reference parsing, and provenance linking (S07)."""

import re

from rag.retrieval.models import Citation, SearchResult


def create_citation_from_chunk(chunk: SearchResult, max_excerpt_len: int = 250) -> Citation:
    """Create a typed Citation from a retrieved SearchResult chunk."""
    clean_text = chunk.text.strip().replace("\n", " ")
    excerpt = clean_text[:max_excerpt_len] + ("..." if len(clean_text) > max_excerpt_len else "")

    return Citation(
        chunk_id=chunk.chunk_id,
        source_title=chunk.metadata.title,
        norm_reference=chunk.metadata.norm_number,
        section_title=chunk.metadata.section_title,
        source_url_or_path=chunk.metadata.source_url_or_path,
        excerpt=excerpt,
    )


def extract_citations(
    synthesized_text: str,
    candidate_chunks: list[SearchResult],
) -> list[Citation]:
    """Extract and link citations referenced in synthesized response text.

    Args:
        synthesized_text: The text returned by the synthesizer.
        candidate_chunks: The candidate chunks provided as context.

    Returns:
        List of unique Citation objects.
    """
    if not candidate_chunks:
        return []

    chunk_map = {chunk.chunk_id: chunk for chunk in candidate_chunks}

    # Match markers like [^chunk_id], [^1], [fonte: chunk_id], [chunk_id]
    explicit_matches = set(re.findall(r"\[\^([a-zA-Z0-9_\-]+)\]", synthesized_text))
    fonte_pattern = r"\[fonte:\s*([a-zA-Z0-9_\-]+)\]"
    fonte_matches = set(re.findall(fonte_pattern, synthesized_text, re.IGNORECASE))
    all_matched_keys = explicit_matches.union(fonte_matches)

    matched_citations: list[Citation] = []
    seen_ids: set[str] = set()

    # 1. Match explicit chunk IDs
    for key in all_matched_keys:
        if key in chunk_map and key not in seen_ids:
            matched_citations.append(create_citation_from_chunk(chunk_map[key]))
            seen_ids.add(key)
        elif key.isdigit():
            # If 1-based index (e.g. [^1]), map to corresponding candidate chunk
            idx = int(key) - 1
            if 0 <= idx < len(candidate_chunks):
                target_chunk = candidate_chunks[idx]
                if target_chunk.chunk_id not in seen_ids:
                    matched_citations.append(create_citation_from_chunk(target_chunk))
                    seen_ids.add(target_chunk.chunk_id)

    # 2. If no explicit markers were inserted by the LLM but chunks were used to answer,
    # link top relevant supporting chunks automatically to guarantee provenance
    if not matched_citations:
        for chunk in candidate_chunks:
            if chunk.chunk_id not in seen_ids:
                matched_citations.append(create_citation_from_chunk(chunk))
                seen_ids.add(chunk.chunk_id)

    return matched_citations
