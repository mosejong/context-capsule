from __future__ import annotations

import re
from collections import Counter

from app.schemas.capsule_schema import RepoChunk, RepoFile

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_가-힣]+")
IMPORTANT_PATH_HINTS = {
    "readme": 1.5,
    "contribution": 1.4,
    "docker": 1.2,
    "auth": 1.4,
    "login": 1.4,
    "schema": 1.3,
    "model": 1.2,
    "router": 1.2,
    "service": 1.1,
    "api": 1.1,
}


def tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def build_chunks(files: list[RepoFile], max_lines: int = 80) -> list[RepoChunk]:
    chunks: list[RepoChunk] = []
    for file in files:
        lines = file.content.splitlines()
        for start in range(0, len(lines), max_lines):
            selected = lines[start : start + max_lines]
            if not any(line.strip() for line in selected):
                continue
            chunks.append(
                RepoChunk(
                    path=file.path,
                    kind=file.kind,
                    text="\n".join(selected).strip(),
                    start_line=start + 1,
                    end_line=start + len(selected),
                )
            )
    return chunks


def retrieve_relevant_chunks(files: list[RepoFile], query: str, top_k: int = 8) -> list[RepoChunk]:
    """Keyword baseline retriever.

    Phase 2 will replace or complement this with vector search.
    """
    chunks = build_chunks(files)
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return chunks[:top_k]

    scored: list[RepoChunk] = []
    for chunk in chunks:
        text_terms = Counter(tokenize(chunk.text + " " + chunk.path))
        score = 0.0
        for term, weight in query_terms.items():
            score += text_terms.get(term, 0) * weight

        lower_path = chunk.path.lower()
        for hint, bonus in IMPORTANT_PATH_HINTS.items():
            if hint in lower_path and hint in query_terms:
                score += bonus

        if score > 0:
            chunk.score = score
            scored.append(chunk)

    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
