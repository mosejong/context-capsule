from __future__ import annotations

import hashlib
import math
import os
from collections import Counter
from typing import Protocol

from app.retrievers.simple_retriever import (
    MANDATORY_SCORE,
    build_chunks,
    classify_task_intent,
    extract_query_paths,
    filter_files_by_scope,
    normalize_path,
    resolve_mentioned_file_paths,
    retrieve_relevant_chunks,
    score_chunk,
    should_exclude_by_intent,
    tokenize,
)
from app.schemas.capsule_schema import RepoChunk, RepoFile

DEFAULT_HASH_DIMENSIONS = 384
DEFAULT_KEYWORD_WEIGHT = 0.58
DEFAULT_SEMANTIC_WEIGHT = 0.42
MIN_SEMANTIC_SCORE = 0.08


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, texts: list[str]) -> list[list[float]]:
        ...


class HashEmbeddingProvider:
    """Dependency-free local embedding provider for closed-network mode.

    This is not a semantic model. It is a deterministic vector baseline that
    lets hybrid ranking run without downloading or calling external services.
    Users can opt into sentence-transformers through an environment variable.
    """

    name = "hash_local_v1"

    def __init__(self, dimensions: int = DEFAULT_HASH_DIMENSIONS) -> None:
        self.dimensions = dimensions

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        terms = tokenize(text)
        if not terms:
            return vector

        counts = Counter(terms)
        for term, count in counts.items():
            digest = hashlib.blake2b(term.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "little") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign * (1.0 + math.log(count))

        return normalize_vector(vector)


class SentenceTransformerEmbeddingProvider:
    name = "sentence_transformers"

    def __init__(self, model_name_or_path: str) -> None:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

        self.model_name_or_path = model_name_or_path
        self.model = SentenceTransformer(model_name_or_path)
        self.name = f"sentence_transformers:{model_name_or_path}"

    def embed(self, texts: list[str]) -> list[list[float]]:
        embeddings = self.model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [list(map(float, embedding)) for embedding in embeddings]


def build_default_embedding_provider() -> EmbeddingProvider:
    model_name = os.getenv("CONTEXT_CAPSULE_EMBEDDING_MODEL")
    if model_name:
        try:
            return SentenceTransformerEmbeddingProvider(model_name)
        except Exception:
            return HashEmbeddingProvider()
    return HashEmbeddingProvider()


def retrieve_hybrid_chunks(
    files: list[RepoFile],
    query: str,
    top_k: int = 8,
    embedding_provider: EmbeddingProvider | None = None,
    keyword_weight: float = DEFAULT_KEYWORD_WEIGHT,
    semantic_weight: float = DEFAULT_SEMANTIC_WEIGHT,
    include_extensions: list[str] | None = None,
    exclude_extensions: list[str] | None = None,
) -> list[RepoChunk]:
    scoped_files = filter_files_by_scope(files, include_extensions, exclude_extensions)
    chunks = build_chunks(scoped_files)
    if not chunks:
        return []

    query_terms = Counter(tokenize(query))
    if not query_terms:
        return retrieve_relevant_chunks(
            scoped_files,
            query,
            top_k=top_k,
            include_extensions=include_extensions,
            exclude_extensions=exclude_extensions,
        )

    query_paths = extract_query_paths(query)
    mentioned_paths = resolve_mentioned_file_paths(scoped_files, query, query_terms, query_paths)
    intent = classify_task_intent(query_terms)
    provider = embedding_provider or build_default_embedding_provider()

    try:
        query_vector = provider.embed([query])[0]
        chunk_vectors = provider.embed([chunk_text(chunk) for chunk in chunks])
    except Exception:
        return retrieve_relevant_chunks(
            scoped_files,
            query,
            top_k=top_k,
            include_extensions=include_extensions,
            exclude_extensions=exclude_extensions,
        )

    best_by_path: dict[str, RepoChunk] = {}
    max_keyword_score = 1.0
    keyword_scores = []
    for chunk in chunks:
        lower_path = normalize_path(chunk.path)
        if should_exclude_by_intent(chunk, lower_path, intent, mentioned_paths):
            keyword_scores.append(0.0)
            continue
        score = score_chunk(chunk, query_terms, query_paths, mentioned_paths, intent)
        keyword_scores.append(score)
        if score < MANDATORY_SCORE:
            max_keyword_score = max(max_keyword_score, score)

    for chunk, keyword_score, vector in zip(chunks, keyword_scores, chunk_vectors, strict=True):
        lower_path = normalize_path(chunk.path)
        if should_exclude_by_intent(chunk, lower_path, intent, mentioned_paths):
            continue
        semantic_score = max(0.0, cosine_similarity(query_vector, vector))

        if lower_path in mentioned_paths:
            final_score = MANDATORY_SCORE + semantic_score
        else:
            normalized_keyword = max(0.0, keyword_score / max_keyword_score)
            final_score = (keyword_weight * normalized_keyword) + (semantic_weight * semantic_score)
            if final_score <= 0 and semantic_score < MIN_SEMANTIC_SCORE:
                continue

        candidate = chunk.model_copy(update={"score": round(final_score * 100.0, 4)})
        current = best_by_path.get(chunk.path)
        if current is None or candidate.score > current.score:
            best_by_path[chunk.path] = candidate

    ranked = sorted(
        best_by_path.values(),
        key=lambda item: (normalize_path(item.path) not in mentioned_paths, -item.score, item.path.lower()),
    )
    return ranked[:top_k] or retrieve_relevant_chunks(
        scoped_files,
        query,
        top_k=top_k,
        include_extensions=include_extensions,
        exclude_extensions=exclude_extensions,
    )


def chunk_text(chunk: RepoChunk) -> str:
    return f"{chunk.path}\n{chunk.text}"


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right:
        return 0.0
    size = min(len(left), len(right))
    numerator = sum(left[index] * right[index] for index in range(size))
    left_norm = math.sqrt(sum(value * value for value in left[:size]))
    right_norm = math.sqrt(sum(value * value for value in right[:size]))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return numerator / (left_norm * right_norm)


def normalize_vector(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if norm == 0:
        return vector
    return [value / norm for value in vector]
