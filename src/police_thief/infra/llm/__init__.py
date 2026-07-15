"""Four interchangeable providers for the verbal "trash talk" layer only
(Sec. 6.5.1, Appendix F Table 21). NEVER used for movement decisions.

Selected via config/<role>/game.toml's [trash_talk] `provider` key:
template (default, 0 tokens) | ollama | claude_api | claude_cli.
"""

from police_thief.infra.llm.base import LLMProvider

__all__ = ["LLMProvider"]
