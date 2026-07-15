"""Highest-cost provider: shells out to `claude -p` via the Claude Code CLI,
subject to the local subscription (Sec. 6.5.1)."""

from __future__ import annotations

from police_thief.infra.llm.base import LLMProvider


class ClaudeCLIProvider(LLMProvider):
    def generate_hint(self, *, prompt: str, word_limit: int) -> str:
        raise NotImplementedError
