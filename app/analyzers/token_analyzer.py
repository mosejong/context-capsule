from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.capsule_schema import RepoChunk, RepoFile, TokenBudget

ASCII_WORD_PATTERN = re.compile(r"[A-Za-z0-9_]+")
HANGUL_PATTERN = re.compile(r"[가-힣]")
NON_SPACE_PATTERN = re.compile(r"\S")


@dataclass(frozen=True)
class TokenUsageInput:
    raw_context: str
    retrieved_context: str
    handoff_prompt: str
    baseline_context_scope: str = "retrieved_file_contents"


class TokenUsageProvider(ABC):
    """Provider boundary for local, external, or provider-reported token usage."""

    name: str
    verification_status: str
    actual_provider_usage: str

    @abstractmethod
    def analyze(self, usage_input: TokenUsageInput) -> TokenBudget:
        """Return token budget numbers for one generated capsule."""


class ApproxLocalTokenUsageProvider(TokenUsageProvider):
    name = "approx_local_v1"
    verification_status = "Estimated only"
    actual_provider_usage = "Not measured yet"

    def analyze(self, usage_input: TokenUsageInput) -> TokenBudget:
        raw_context_tokens = estimate_tokens(usage_input.raw_context)
        retrieved_context_tokens = estimate_tokens(usage_input.retrieved_context)
        handoff_prompt_tokens = estimate_tokens(usage_input.handoff_prompt)
        reduction = calculate_reduction(raw_context_tokens, handoff_prompt_tokens)

        return TokenBudget(
            raw_context_tokens=raw_context_tokens,
            retrieved_context_tokens=retrieved_context_tokens,
            handoff_prompt_tokens=handoff_prompt_tokens,
            estimated_reduction_percent=reduction,
            method=self.name,
            baseline_context_scope=usage_input.baseline_context_scope,
            verification_status=self.verification_status,
            actual_provider_usage=self.actual_provider_usage,
        )


class ExternalTokenAnalyzerProvider(TokenUsageProvider):
    """Placeholder adapter for the upcoming allthatai/Token-analyzer project."""

    name = "external_token_analyzer_pending"
    verification_status = "Adapter pending"
    actual_provider_usage = "Not measured yet"

    def analyze(self, usage_input: TokenUsageInput) -> TokenBudget:  # pragma: no cover - intentionally unavailable
        raise NotImplementedError(
            "External Token-analyzer adapter is waiting for the upstream open-source API and license."
        )


def estimate_tokens(text: str) -> int:
    """Return a lightweight token estimate without external tokenizer deps.

    This is intentionally approximate. Provider-specific tokenizers can be
    added behind TokenUsageProvider implementations later.
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
    provider: TokenUsageProvider | None = None,
) -> TokenBudget:
    usage_input = build_token_usage_input(files, relevant_chunks, handoff_prompt)
    provider = provider or ApproxLocalTokenUsageProvider()
    return provider.analyze(usage_input)


def build_token_usage_input(
    files: list[RepoFile],
    relevant_chunks: list[RepoChunk],
    handoff_prompt: str,
) -> TokenUsageInput:
    raw_context, baseline_context_scope = build_raw_context_baseline(files, relevant_chunks)
    return TokenUsageInput(
        raw_context=raw_context,
        retrieved_context="\n\n".join(chunk.text for chunk in relevant_chunks),
        handoff_prompt=handoff_prompt,
        baseline_context_scope=baseline_context_scope,
    )


def build_raw_context_baseline(files: list[RepoFile], relevant_chunks: list[RepoChunk]) -> tuple[str, str]:
    """Use selected file contents as the token baseline, not the whole repo.

    This keeps the token comparison honest: Context Capsule is claiming that
    it can narrow a task to candidate files/chunks, not that every task would
    otherwise paste the entire repository into an AI tool.
    """
    files_by_path = {file.path: file for file in files}
    selected_paths: list[str] = []
    seen = set()
    for chunk in relevant_chunks:
        if chunk.path in seen:
            continue
        if chunk.path not in files_by_path:
            continue
        seen.add(chunk.path)
        selected_paths.append(chunk.path)

    selected_contents = [files_by_path[path].content for path in selected_paths]
    if selected_contents:
        return "\n\n".join(selected_contents), "retrieved_file_contents"

    return "\n\n".join(file.content for file in files), "scanned_repository_fallback"


def calculate_reduction(original_tokens: int, capsule_tokens: int) -> float:
    if original_tokens <= 0:
        return 0.0
    reduction = 100 * (1 - (capsule_tokens / original_tokens))
    return round(max(reduction, 0.0), 1)
