"""Common interface all four trash-talk providers implement."""

from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    def generate_hint(self, *, prompt: str, word_limit: int) -> str:
        """Produce a verbal hint (true or a calculated bluff), capped at
        `word_limit` words (default 15, Appendix F Table 14)."""
        raise NotImplementedError
