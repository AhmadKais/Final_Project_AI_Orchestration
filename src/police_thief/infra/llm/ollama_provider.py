"""Local model via Ollama (e.g. localhost:11434) -- zero API tokens, no rate limit."""

from __future__ import annotations

from police_thief.infra.llm.base import LLMProvider


class OllamaProvider(LLMProvider):
    def __init__(self, *, base_url: str = "http://localhost:11434", model: str = "llama3"):
        self.base_url = base_url
        self.model = model

    def generate_hint(self, *, prompt: str, word_limit: int) -> str:
        raise NotImplementedError
