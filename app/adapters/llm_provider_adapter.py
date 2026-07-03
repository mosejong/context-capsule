from __future__ import annotations

import json
import os
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol


NVIDIA_NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"


def load_local_env() -> None:
    try:
        from dotenv import load_dotenv
    except Exception:
        return

    dotenv_path = Path.cwd() / ".env"
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int = 0
    output_tokens: int = 0
    cache_creation_input_tokens: int = 0
    cache_read_input_tokens: int = 0


@dataclass(frozen=True)
class LLMResponse:
    text: str
    usage: LLMUsage | None = None


class LLMProvider(Protocol):
    name: str

    def complete(self, *, system: str, user: str, model: str, max_tokens: int = 512) -> LLMResponse:
        ...


class AnthropicProvider:
    name = "anthropic"

    def __init__(self, api_key: str | None = None) -> None:
        load_local_env()
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY is required for anthropic provider")
        import anthropic  # type: ignore[import-not-found]

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def complete(self, *, system: str, user: str, model: str, max_tokens: int = 512) -> LLMResponse:
        message = self.client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return LLMResponse(text=message.content[0].text, usage=usage_from_anthropic(message.usage))


class NvidiaNimProvider:
    name = "nvidia_nim"

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        load_local_env()
        self.api_key = api_key or os.getenv("NVIDIA_API_KEY", "")
        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY is required for nvidia provider")
        self.base_url = (base_url or os.getenv("NVIDIA_NIM_BASE_URL") or NVIDIA_NIM_BASE_URL).rstrip("/")

    def complete(self, *, system: str, user: str, model: str, max_tokens: int = 512) -> LLMResponse:
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.2,
            "top_p": 0.95,
            "max_tokens": max_tokens,
            "stream": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=120) as response:  # noqa: S310 - user-provided endpoint is explicit.
            body = response.read().decode("utf-8")
        data = json.loads(body)
        return LLMResponse(text=extract_openai_compatible_text(data), usage=usage_from_openai_compatible(data.get("usage")))


def build_llm_provider(provider: str) -> LLMProvider:
    normalized = provider.strip().lower()
    if normalized == "anthropic":
        return AnthropicProvider()
    if normalized in {"nvidia", "nvidia_nim", "nim"}:
        return NvidiaNimProvider()
    raise ValueError(f"Unsupported provider: {provider}")


def default_models_for_provider(provider: str) -> list[str]:
    normalized = provider.strip().lower()
    if normalized == "anthropic":
        return [
            "claude-haiku-4-5-20251001",
            "claude-sonnet-4-6",
            "claude-opus-4-8",
        ]
    if normalized in {"nvidia", "nvidia_nim", "nim"}:
        return [
            "nvidia/nemotron-3-ultra-550b-a55b",
            "deepseek-ai/deepseek-v4-flash",
        ]
    raise ValueError(f"Unsupported provider: {provider}")


def usage_from_anthropic(usage: Any) -> LLMUsage:
    return LLMUsage(
        input_tokens=int(getattr(usage, "input_tokens", 0) or 0),
        output_tokens=int(getattr(usage, "output_tokens", 0) or 0),
        cache_creation_input_tokens=int(getattr(usage, "cache_creation_input_tokens", 0) or 0),
        cache_read_input_tokens=int(getattr(usage, "cache_read_input_tokens", 0) or 0),
    )


def usage_from_openai_compatible(usage: dict[str, Any] | None) -> LLMUsage | None:
    if not usage:
        return None
    return LLMUsage(
        input_tokens=int(usage.get("prompt_tokens") or usage.get("input_tokens") or 0),
        output_tokens=int(usage.get("completion_tokens") or usage.get("output_tokens") or 0),
    )


def extract_openai_compatible_text(data: dict[str, Any]) -> str:
    choices = data.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(str(part.get("text", "")) if isinstance(part, dict) else str(part) for part in content)
    return ""
