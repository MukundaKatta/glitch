"""Multi-model adapter layer providing a unified generation interface."""

from __future__ import annotations

import os
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    """Metadata about a model being evaluated."""

    name: str
    provider: str
    model_id: str
    parameters: dict[str, str | int | float] = Field(default_factory=dict)


class ModelAdapter(ABC):
    """Unified interface for LLM generation."""

    info: ModelInfo

    @abstractmethod
    def generate(self, prompt: str, *, system: str | None = None) -> str:
        """Send a prompt to the model and return the text response."""
        ...

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.info.model_id}>"


class ClaudeAdapter(ModelAdapter):
    """Adapter for Anthropic Claude models."""

    def __init__(
        self,
        model_id: str = "claude-sonnet-4-20250514",
        *,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self.max_tokens = max_tokens
        self.info = ModelInfo(
            name="Claude",
            provider="anthropic",
            model_id=model_id,
            parameters={"max_tokens": max_tokens},
        )

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        import anthropic

        client = anthropic.Anthropic(api_key=self.api_key)
        kwargs: dict = {
            "model": self.info.model_id,
            "max_tokens": self.max_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system:
            kwargs["system"] = system
        message = client.messages.create(**kwargs)
        return message.content[0].text


class OpenAIAdapter(ModelAdapter):
    """Adapter for OpenAI models."""

    def __init__(
        self,
        model_id: str = "gpt-4o",
        *,
        api_key: str | None = None,
        max_tokens: int = 1024,
    ) -> None:
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.max_tokens = max_tokens
        self.info = ModelInfo(
            name="OpenAI",
            provider="openai",
            model_id=model_id,
            parameters={"max_tokens": max_tokens},
        )

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        import openai

        client = openai.OpenAI(api_key=self.api_key)
        messages: list[dict[str, str]] = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        response = client.chat.completions.create(
            model=self.info.model_id,
            messages=messages,
            max_tokens=self.max_tokens,
        )
        return response.choices[0].message.content or ""


class OllamaAdapter(ModelAdapter):
    """Adapter for locally-hosted Ollama models."""

    def __init__(
        self,
        model_id: str = "llama3",
        *,
        base_url: str = "http://localhost:11434",
        max_tokens: int = 1024,
    ) -> None:
        self.base_url = base_url
        self.max_tokens = max_tokens
        self.info = ModelInfo(
            name="Ollama",
            provider="ollama",
            model_id=model_id,
            parameters={"max_tokens": max_tokens},
        )

    def generate(self, prompt: str, *, system: str | None = None) -> str:
        import urllib.request
        import json

        payload: dict = {
            "model": self.info.model_id,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": self.max_tokens},
        }
        if system:
            payload["system"] = system

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req) as resp:
            body = json.loads(resp.read().decode())
        return body.get("response", "")


def get_adapter(provider: str, model_id: str | None = None) -> ModelAdapter:
    """Factory function to create the appropriate adapter."""
    provider = provider.lower()
    defaults: dict[str, tuple[type[ModelAdapter], str]] = {
        "claude": (ClaudeAdapter, "claude-sonnet-4-20250514"),
        "anthropic": (ClaudeAdapter, "claude-sonnet-4-20250514"),
        "openai": (OpenAIAdapter, "gpt-4o"),
        "gpt-4": (OpenAIAdapter, "gpt-4o"),
        "gpt-4o": (OpenAIAdapter, "gpt-4o"),
        "ollama": (OllamaAdapter, "llama3"),
    }
    if provider not in defaults:
        raise ValueError(
            f"Unknown provider '{provider}'. Supported: {sorted(defaults.keys())}"
        )
    adapter_cls, default_model = defaults[provider]
    return adapter_cls(model_id or default_model)
