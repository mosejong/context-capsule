from __future__ import annotations

import re
from collections import Counter

from app.schemas.capsule_schema import FileKind, RepoChunk, RepoFile

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_]+|[\uac00-\ud7a3]+")
PATH_PATTERN = re.compile(r"(?:[\w.-]+[\\/])+[\w.-]+\.[A-Za-z0-9_]+|[\w.-]+\.[A-Za-z0-9_]+")
DOCUMENTATION_HINTS = {
    "doc",
    "docs",
    "documentation",
    "guide",
    "markdown",
    "portfolio",
    "readme",
    "release",
    "summary",
    "\ub2e4\ub4ec",
    "\ubb38\uc11c",
    "\uc124\uba85",
    "\uc694\uc57d",
    "\uc815\ub9ac",
    "\ud3ec\ud2b8\ud3f4\ub9ac\uc624",
}
CODE_HINTS = {
    "adapter",
    "api",
    "bug",
    "cli",
    "code",
    "create-issue",
    "error",
    "fix",
    "function",
    "implement",
    "retriever",
    "test",
    "vector",
    "\uace0\uccd0",
    "\uad6c\ud604",
    "\uc218\uc815",
    "\uc624\ub958",
}
IMPORTANT_PATH_HINTS = {
    "adapter": 2.0,
    "api": 1.2,
    "auth": 1.5,
    "cli": 2.0,
    "contribution": 1.4,
    "docker": 1.2,
    "login": 1.5,
    "model": 1.1,
    "readme": 2.5,
    "retriever": 2.0,
    "router": 1.1,
    "schema": 1.2,
    "service": 1.1,
}
MANDATORY_SCORE = 1000.0
STOP_QUERY_TERMS = {"a", "an", "and", "app", "in", "md", "of", "py", "src", "the", "txt"}


def tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    for raw_token in TOKEN_PATTERN.findall(text):
        token = raw_token.lower()
        tokens.append(token)
        if "_" in token:
            tokens.extend(part for part in token.split("_") if part)
        if "-" in token:
            tokens.extend(part for part in token.split("-") if part)
        if token.endswith("s") and len(token) > 3:
            tokens.append(token[:-1])
    return tokens


def normalize_path(path: str) -> str:
    return path.replace("\\", "/").strip().lower()


def extract_query_paths(text: str) -> set[str]:
    return {normalize_path(match.group(0)) for match in PATH_PATTERN.finditer(text)}


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
    """Keyword/path baseline retriever with mandatory file inclusion.

    This is still a local No-AI baseline, not semantic embedding search. The
    hotfix rule is deliberate: if a user explicitly names a file that exists in
    the repo, that file must be present at the top of the context.
    """
    chunks = build_chunks(files)
    if not chunks:
        return []

    query_terms = Counter(tokenize(query))
    if not query_terms:
        return dedupe_by_file(chunks, top_k)

    query_paths = extract_query_paths(query)
    mentioned_paths = resolve_mentioned_file_paths(files, query, query_terms, query_paths)
    intent = classify_task_intent(query_terms)
    best_by_path: dict[str, RepoChunk] = {}

    for chunk in chunks:
        score = score_chunk(chunk, query_terms, query_paths, mentioned_paths, intent)
        if score <= 0 and normalize_path(chunk.path) not in mentioned_paths:
            continue
        candidate = chunk.model_copy(update={"score": score})
        current = best_by_path.get(chunk.path)
        if current is None or candidate.score > current.score:
            best_by_path[chunk.path] = candidate

    ranked = sorted(
        best_by_path.values(),
        key=lambda item: (normalize_path(item.path) not in mentioned_paths, -item.score, item.path.lower()),
    )
    return ranked[:top_k]


def score_chunk(
    chunk: RepoChunk,
    query_terms: Counter[str],
    query_paths: set[str],
    mentioned_paths: set[str],
    intent: str,
) -> float:
    lower_path = normalize_path(chunk.path)
    if lower_path in mentioned_paths:
        return MANDATORY_SCORE + path_specificity_score(lower_path)

    text_terms = Counter(tokenize(chunk.text + " " + chunk.path))
    score = 0.0
    for term, weight in query_terms.items():
        if term in STOP_QUERY_TERMS:
            continue
        score += text_terms.get(term, 0) * weight

    for hint, bonus in IMPORTANT_PATH_HINTS.items():
        if hint in lower_path and hint in query_terms:
            score += bonus

    score += intent_adjustment(chunk, lower_path, intent, query_terms)
    if query_paths and not path_has_specific_query_overlap(lower_path, query_paths) and score < 5.0:
        return 0.0
    return score


def resolve_mentioned_file_paths(
    files: list[RepoFile],
    query: str,
    query_terms: Counter[str],
    query_paths: set[str],
) -> set[str]:
    lower_query = normalize_path(query)
    mentioned: set[str] = set()
    for file in files:
        lower_path = normalize_path(file.path)
        name = lower_path.rsplit("/", 1)[-1]
        stem = name.rsplit(".", 1)[0]

        if lower_path in query_paths or name in query_paths:
            mentioned.add(lower_path)
            continue
        if lower_path in lower_query or name in lower_query:
            mentioned.add(lower_path)
            continue
        if stem in query_terms and is_specific_stem(stem):
            mentioned.add(lower_path)
            continue
        if name == "readme.md" and "readme" in query_terms:
            mentioned.add(lower_path)

    return mentioned


def classify_task_intent(query_terms: Counter[str]) -> str:
    terms = set(query_terms)
    if terms & DOCUMENTATION_HINTS:
        return "documentation"
    if terms & CODE_HINTS:
        return "code"
    return "general"


def intent_adjustment(chunk: RepoChunk, lower_path: str, intent: str, query_terms: Counter[str]) -> float:
    if intent == "documentation":
        if lower_path.endswith("readme.md"):
            return 9.0
        if lower_path.startswith("docs/") or chunk.kind == FileKind.DOC:
            return 5.0
        if lower_path.startswith("examples/"):
            return 2.0
        if chunk.kind in {FileKind.CODE, FileKind.TEST}:
            return -4.0

    if intent == "code":
        if chunk.kind == FileKind.CODE:
            return 3.0
        if chunk.kind == FileKind.TEST:
            return 1.5
        if chunk.kind == FileKind.DOC and not {"readme", "docs", "documentation"} & set(query_terms):
            return -2.0

    return 0.0


def path_has_specific_query_overlap(lower_path: str, query_paths: set[str]) -> bool:
    path_terms = set(tokenize(lower_path)) - {"app", "src", "test", "tests", "py", "md", "txt"}
    for query_path in query_paths:
        query_terms = set(tokenize(query_path)) - {"app", "src", "test", "tests", "py", "md", "txt"}
        if lower_path in query_path or query_path in lower_path or path_terms & query_terms:
            return True
    return False


def path_specificity_score(lower_path: str) -> float:
    return min(len(lower_path.split("/")) * 2.0, 12.0)


def is_specific_stem(stem: str) -> bool:
    if len(stem) < 4:
        return False
    return stem not in {"main", "test", "index", "init", "__init__"}


def dedupe_by_file(chunks: list[RepoChunk], top_k: int) -> list[RepoChunk]:
    result = []
    seen = set()
    for chunk in chunks:
        if chunk.path in seen:
            continue
        seen.add(chunk.path)
        result.append(chunk)
        if len(result) >= top_k:
            break
    return result
