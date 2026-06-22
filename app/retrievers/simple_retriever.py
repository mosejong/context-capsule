from __future__ import annotations

import re
from collections import Counter

from app.schemas.capsule_schema import RepoChunk, RepoFile

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_가-힣]+")
PATH_PATTERN = re.compile(r"(?:[\w.-]+[\\/])+[\w.-]+\.[A-Za-z0-9_]+")
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
PATH_QUERY_MIN_SCORE = 10.0


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw_token in TOKEN_PATTERN.findall(text):
        token = raw_token.lower()
        tokens.append(token)
        if "_" in token:
            tokens.extend(part for part in token.split("_") if part)
        if token.endswith("s") and len(token) > 3:
            tokens.append(token[:-1])
    return tokens


def extract_query_paths(text: str) -> set[str]:
    return {match.group(0).replace("\\", "/").lower() for match in PATH_PATTERN.finditer(text)}


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
    query_paths = extract_query_paths(query)
    if not query_terms:
        return chunks[:top_k]

    scored: list[RepoChunk] = []
    for chunk in chunks:
        text_terms = Counter(tokenize(chunk.text + " " + chunk.path))
        score = 0.0
        for term, weight in query_terms.items():
            score += text_terms.get(term, 0) * weight

        lower_path = chunk.path.lower()
        exact_path_match = lower_path in query_paths
        if exact_path_match:
            score += 20.0

        for hint, bonus in IMPORTANT_PATH_HINTS.items():
            if hint in lower_path and hint in query_terms:
                score += bonus

        if score > 0 and (not query_paths or exact_path_match or score >= PATH_QUERY_MIN_SCORE):
            chunk.score = score
            scored.append(chunk)

    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
