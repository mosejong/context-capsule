from __future__ import annotations

import math
import re

from app.schemas.capsule_schema import RepoChunk, RepoFile, TokenBudget

ASCII_WORD_PATTERN = re.compile(r"[A-Za-z0-9_]+")
HANGUL_PATTERN = re.compile(r"[가-힣]")
NON_SPACE_PATTERN = re.compile(r"\S")


def estimate_tokens(text: str) -> int:
    """Return a lightweight token estimate without external tokenizer deps.

    This is intentionally approximate. Provider-specific tokenizers can be
    added behind the same interface later.
    """
    if not text:
        return 0

    ascii_words = ASCII_WORD_PATTERN.findall(text)
    hangul_chars = HANGUL_PATTERN.findall(text)
    non_space_chars = NON_SPACE_PATTERN.findall(text)
    ascii_chars = sum(len(word) for word in ascii_words)
    hangul_count = len(hangul_chars)
    other_chars = max(len(non_space_chars) - ascii_chars - hangul_count, 0)

    estimated = (len(ascii_words) * 1.15) + (hangul_count * 0.9) + (other_chars * 0.35)
    return max(1, math.ceil(estimated))


def analyze_token_budget(
    files: list[RepoFile],
    relevant_chunks: list[RepoChunk],
    handoff_prompt: str,
) -> TokenBudget:
    raw_context = "\n\n".join(file.content for file in files)
    retrieved_context = "\n\n".join(chunk.text for chunk in relevant_chunks)

    raw_context_tokens = estimate_tokens(raw_context)
    retrieved_context_tokens = estimate_tokens(retrieved_context)
    handoff_prompt_tokens = estimate_tokens(handoff_prompt)
    reduction = calculate_reduction(raw_context_tokens, handoff_prompt_tokens)

    return TokenBudget(
        raw_context_tokens=raw_context_tokens,
        retrieved_context_tokens=retrieved_context_tokens,
        handoff_prompt_tokens=handoff_prompt_tokens,
        estimated_reduction_percent=reduction,
        method="approx_local_v1",
    )


def calculate_reduction(original_tokens: int, capsule_tokens: int) -> float:
    if original_tokens <= 0:
        return 0.0
    reduction = 100 * (1 - (capsule_tokens / original_tokens))
    return round(max(reduction, 0.0), 1)
