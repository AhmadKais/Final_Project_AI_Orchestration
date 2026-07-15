"""Step-0 hardware/software declaration for computational fairness (Sec. 5.5).

Collects OS, CPU core count/frequency, RAM, GPU/VRAM presence, the LLM in
use, code version, and the GitHub commit hash actually played -- packed into
a JSON string and signed before the first move.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Step0Declaration:
    os_name: str
    cpu_cores: int
    cpu_freq_mhz: float
    ram_gb: float
    gpu: str | None
    vram_gb: float | None
    llm_model: str
    code_version: str
    github_commit: str
    group_name: str
    sub_game_number: int


def collect_step0_declaration(*, code_version: str, github_commit: str,
                               group_name: str, sub_game_number: int,
                               llm_model: str) -> Step0Declaration:
    """Gather live hardware/software facts for this machine."""
    raise NotImplementedError


def sign_declaration(declaration: Step0Declaration, signing_key: bytes) -> str:
    """Cryptographically sign the declaration so it cannot be forged after the fact."""
    raise NotImplementedError
