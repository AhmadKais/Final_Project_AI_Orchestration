"""Default provider: pre-written Python-side sentences, zero tokens, no
network dependency (Sec. 6.5.1). Recommended default -- keeps full budget
on the movement algorithm.
"""

from __future__ import annotations

from police_thief.infra.llm.base import LLMProvider


class TemplateProvider(LLMProvider):
    def generate_hint(self, *, prompt: str, word_limit: int) -> str:
        raise NotImplementedError
