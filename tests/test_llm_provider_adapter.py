import json
import os
import sys
from types import SimpleNamespace

import pytest

from app.adapters import llm_provider_adapter as adapter
from app.adapters.llm_provider_adapter import (
    DEFAULT_TEMPERATURE,
    DEFAULT_TOP_P,
    AnthropicProvider,
    NvidiaNimProvider,
    default_models_for_provider,
    extract_openai_compatible_text,
    usage_from_openai_compatible,
)


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None

    def read(self) -> bytes:
        return json.dumps(self.payload).encode("utf-8")


def test_default_nvidia_models_are_openai_compatible_ids():
    models = default_models_for_provider("nvidia")

    assert "nvidia/nemotron-3-ultra-550b-a55b" in models
    assert "deepseek-ai/deepseek-v4-flash" in models


def test_nvidia_provider_requires_key(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NVIDIA_API_KEY", raising=False)

    with pytest.raises(ValueError, match="NVIDIA_API_KEY"):
        NvidiaNimProvider()


def test_nvidia_provider_loads_key_from_local_env_file(monkeypatch, tmp_path):
    original_key = os.environ.pop("NVIDIA_API_KEY", None)
    try:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".env").write_text('NVIDIA_API_KEY = "nvapi-from-dotenv"\n', encoding="utf-8")

        provider = NvidiaNimProvider(base_url="https://example.test/v1")

        assert provider.api_key == "nvapi-from-dotenv"
    finally:
        os.environ.pop("NVIDIA_API_KEY", None)
        if original_key is not None:
            os.environ["NVIDIA_API_KEY"] = original_key


def test_nvidia_provider_posts_openai_compatible_payload_without_leaking_key(monkeypatch):
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["timeout"] = timeout
        captured["authorization"] = request.get_header("Authorization")
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeResponse(
            {
                "choices": [{"message": {"content": "README.md부터 확인하세요."}}],
                "usage": {"prompt_tokens": 12, "completion_tokens": 5},
            }
        )

    monkeypatch.setattr(adapter.urllib.request, "urlopen", fake_urlopen)
    provider = NvidiaNimProvider(api_key="nvapi-test-secret", base_url="https://example.test/v1")

    response = provider.complete(
        system="system rules",
        user="리드미 손보자",
        model="nvidia/nemotron-3-ultra-550b-a55b",
        max_tokens=64,
    )

    assert captured["url"] == "https://example.test/v1/chat/completions"
    assert captured["timeout"] == 120
    assert captured["authorization"] == "Bearer nvapi-test-secret"
    assert captured["body"]["model"] == "nvidia/nemotron-3-ultra-550b-a55b"
    assert captured["body"]["messages"][0] == {"role": "system", "content": "system rules"}
    assert captured["body"]["messages"][1] == {"role": "user", "content": "리드미 손보자"}
    assert captured["body"]["stream"] is False
    assert response.text == "README.md부터 확인하세요."
    assert response.usage is not None
    assert response.usage.input_tokens == 12
    assert response.usage.output_tokens == 5
    assert "nvapi-test-secret" not in response.text


def test_anthropic_provider_uses_same_sampling_parameters(monkeypatch):
    captured = {}

    class FakeMessages:
        def create(self, **kwargs):
            captured.update(kwargs)
            return SimpleNamespace(
                content=[SimpleNamespace(text="ok")],
                usage=SimpleNamespace(input_tokens=1, output_tokens=1),
            )

    class FakeAnthropicClient:
        def __init__(self, api_key):
            self.api_key = api_key
            self.messages = FakeMessages()

    fake_module = SimpleNamespace(Anthropic=FakeAnthropicClient)
    monkeypatch.setitem(sys.modules, "anthropic", fake_module)

    provider = AnthropicProvider(api_key="anthropic-test-key")
    response = provider.complete(system="system", user="user", model="claude-test", max_tokens=32)

    assert response.text == "ok"
    assert captured["temperature"] == DEFAULT_TEMPERATURE
    assert captured["top_p"] == DEFAULT_TOP_P
    assert captured["max_tokens"] == 32


def test_extract_openai_compatible_text_handles_text_parts():
    text = extract_openai_compatible_text(
        {
            "choices": [
                {
                    "message": {
                        "content": [
                            {"type": "text", "text": "첫 문장"},
                            {"type": "text", "text": " 둘째 문장"},
                        ]
                    }
                }
            ]
        }
    )

    assert text == "첫 문장 둘째 문장"


def test_usage_from_openai_compatible_accepts_openai_and_input_output_names():
    openai_usage = usage_from_openai_compatible({"prompt_tokens": 10, "completion_tokens": 4})
    input_output_usage = usage_from_openai_compatible({"input_tokens": 8, "output_tokens": 3})

    assert openai_usage is not None
    assert openai_usage.input_tokens == 10
    assert openai_usage.output_tokens == 4
    assert input_output_usage is not None
    assert input_output_usage.input_tokens == 8
    assert input_output_usage.output_tokens == 3
