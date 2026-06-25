from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from app.retrievers.hybrid_retriever import (
    EmbeddingProvider,
    build_default_embedding_provider,
    chunk_text,
    retrieve_hybrid_chunks,
)
from app.retrievers.simple_retriever import (
    MANDATORY_SCORE,
    build_chunks,
    classify_task_intent,
    extract_query_paths,
    filter_files_by_scope,
    normalize_path,
    normalize_extensions,
    path_allowed_by_scope,
    resolve_mentioned_file_paths,
    score_chunk,
    should_exclude_by_intent,
    tokenize,
)
from app.schemas.capsule_schema import FileKind, RepoChunk, RepoFile

INDEX_VERSION = 1
DEFAULT_INDEX_DIRNAME = ".context-capsule-index"
DEFAULT_INDEX_FILENAME = "retrieval_index.json"


@dataclass(frozen=True)
class RetrievalIndexBuildResult:
    index_path: Path
    provider_name: str
    file_count: int
    chunk_count: int


@dataclass(frozen=True)
class IndexedRetrievalResult:
    chunks: list[RepoChunk]
    used_mode: str
    fallback_reason: str | None
    index_path: Path


def default_index_path(repo_path: Path | str) -> Path:
    return Path(repo_path) / DEFAULT_INDEX_DIRNAME / DEFAULT_INDEX_FILENAME


def build_retrieval_index(
    files: list[RepoFile],
    repo_path: Path | str,
    index_path: Path | None = None,
    embedding_provider: EmbeddingProvider | None = None,
) -> RetrievalIndexBuildResult:
    provider = embedding_provider or build_default_embedding_provider()
    chunks = build_chunks(files)
    embeddings = provider.embed([chunk_text(chunk) for chunk in chunks]) if chunks else []
    path = index_path or default_index_path(repo_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "version": INDEX_VERSION,
        "built_at": datetime.now().isoformat(timespec="seconds"),
        "provider": provider.name,
        "files": [file_metadata(file) for file in files],
        "chunks": [
            {
                "path": chunk.path,
                "kind": chunk.kind.value,
                "text": chunk.text,
                "start_line": chunk.start_line,
                "end_line": chunk.end_line,
                "embedding": embedding,
            }
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ],
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return RetrievalIndexBuildResult(
        index_path=path,
        provider_name=provider.name,
        file_count=len(files),
        chunk_count=len(chunks),
    )


def retrieve_indexed_chunks(
    files: list[RepoFile],
    query: str,
    repo_path: Path | str,
    top_k: int = 8,
    index_path: Path | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    include_extensions: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
) -> list[RepoChunk]:
    return retrieve_indexed_chunks_with_report(
        files,
        query,
        repo_path,
        top_k=top_k,
        index_path=index_path,
        embedding_provider=embedding_provider,
        include_extensions=include_extensions,
        exclude_extensions=exclude_extensions,
    ).chunks


def retrieve_indexed_chunks_with_report(
    files: list[RepoFile],
    query: str,
    repo_path: Path | str,
    top_k: int = 8,
    index_path: Path | None = None,
    embedding_provider: EmbeddingProvider | None = None,
    include_extensions: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
) -> IndexedRetrievalResult:
    path = index_path or default_index_path(repo_path)
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        validate_index_payload(payload, files)
        provider = embedding_provider or build_default_embedding_provider()
        if payload.get("provider") != provider.name:
            raise ValueError("retrieval index provider mismatch")
        query_vector = provider.embed([query])[0]
        chunks, chunk_payloads = scope_indexed_chunks(
            payload_to_chunks(payload),
            payload["chunks"],
            include_extensions,
            exclude_extensions,
        )
        scoped_files = filter_files_by_scope(files, include_extensions, exclude_extensions)
        ranked = rank_indexed_chunks(scoped_files, chunks, chunk_payloads, query, query_vector, top_k)
        if ranked:
            return IndexedRetrievalResult(
                chunks=ranked,
                used_mode="indexed",
                fallback_reason=None,
                index_path=path,
            )
        fallback = retrieve_hybrid_chunks(
            files,
            query,
            top_k=top_k,
            embedding_provider=provider,
            include_extensions=include_extensions,
            exclude_extensions=exclude_extensions,
        )
        return IndexedRetrievalResult(
            chunks=fallback,
            used_mode="hybrid_fallback",
            fallback_reason="indexed retrieval returned no ranked chunks",
            index_path=path,
        )
    except Exception as exc:
        fallback = retrieve_hybrid_chunks(
            files,
            query,
            top_k=top_k,
            embedding_provider=embedding_provider,
            include_extensions=include_extensions,
            exclude_extensions=exclude_extensions,
        )
        return IndexedRetrievalResult(
            chunks=fallback,
            used_mode="hybrid_fallback",
            fallback_reason=str(exc),
            index_path=path,
        )


def validate_index_payload(payload: dict[str, Any], files: list[RepoFile]) -> None:
    if payload.get("version") != INDEX_VERSION:
        raise ValueError("unsupported index version")
    indexed_files = {item["path"]: item for item in payload.get("files", [])}
    current_files = {file.path: file_metadata(file) for file in files}
    if indexed_files != current_files:
        raise ValueError("retrieval index is stale")


def payload_to_chunks(payload: dict[str, Any]) -> list[RepoChunk]:
    chunks = []
    for item in payload.get("chunks", []):
        chunks.append(
            RepoChunk(
                path=item["path"],
                kind=FileKind(item["kind"]),
                text=item["text"],
                start_line=item.get("start_line"),
                end_line=item.get("end_line"),
            )
        )
    return chunks


def scope_indexed_chunks(
    chunks: list[RepoChunk],
    payloads: list[dict[str, Any]],
    include_extensions: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
) -> tuple[list[RepoChunk], list[dict[str, Any]]]:
    include = normalize_extensions(include_extensions)
    exclude = normalize_extensions(exclude_extensions)
    if not include and not exclude:
        return chunks, payloads
    scoped_chunks: list[RepoChunk] = []
    scoped_payloads: list[dict[str, Any]] = []
    for chunk, payload in zip(chunks, payloads, strict=True):
        if path_allowed_by_scope(chunk.path, include, exclude):
            scoped_chunks.append(chunk)
            scoped_payloads.append(payload)
    return scoped_chunks, scoped_payloads


def rank_indexed_chunks(
    files: list[RepoFile],
    chunks: list[RepoChunk],
    chunk_payloads: list[dict[str, Any]],
    query: str,
    query_vector: list[float],
    top_k: int,
) -> list[RepoChunk]:
    from collections import Counter

    query_terms = Counter(tokenize(query))
    query_paths = extract_query_paths(query)
    mentioned_paths = resolve_mentioned_file_paths(files, query, query_terms, query_paths)
    intent = classify_task_intent(query_terms)
    best_by_path: dict[str, RepoChunk] = {}
    for chunk, payload in zip(chunks, chunk_payloads, strict=True):
        lower_path = normalize_path(chunk.path)
        if should_exclude_by_intent(chunk, lower_path, intent, mentioned_paths):
            continue
        semantic_score = max(0.0, cosine_similarity(query_vector, payload.get("embedding", [])))
        keyword_score = max(0.0, score_chunk(chunk, query_terms, query_paths, mentioned_paths, intent))
        if lower_path in mentioned_paths:
            score = MANDATORY_SCORE + semantic_score
        else:
            score = semantic_score + min(keyword_score / 100.0, 1.0)
        if score <= 0:
            continue
        candidate = chunk.model_copy(update={"score": round(score * 100.0, 4)})
        current = best_by_path.get(chunk.path)
        if current is None or candidate.score > current.score:
            best_by_path[chunk.path] = candidate
    return sorted(best_by_path.values(), key=lambda item: (-item.score, item.path.lower()))[:top_k]


def file_metadata(file: RepoFile) -> dict[str, Any]:
    return {
        "path": file.path,
        "kind": file.kind.value,
        "size": file.size,
        "sha256": hashlib.sha256(file.content.encode("utf-8")).hexdigest(),
    }


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    numerator = sum(float(left[index]) * float(right[index]) for index in range(size))
    left_norm = sum(float(value) * float(value) for value in left[:size]) ** 0.5
    right_norm = sum(float(value) * float(value) for value in right[:size]) ** 0.5
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)
