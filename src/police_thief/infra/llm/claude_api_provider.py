"""Cloud model via the Anthropic API (e.g. Haiku) -- real token consumption,
counted against token_budget_per_series (Appendix F Table 18)."""

from __future__ import annotations

from police_thief.infra.llm.base import LLMProvider


class ClaudeAPIProvider(LLMProvider):
    def __init__(self, *, model: str = "claude-haiku-4-5", api_key: str | None = None):
        self.model = model
        self.api_key = api_key

    def generate_hint(self, *, prompt: str, word_limit: int) -> str:
        raise NotImplementedError
