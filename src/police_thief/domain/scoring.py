"""Translate a GameOutcome into the asymmetric point award (Table 2 / Appendix F Table 17).

Defaults (all "Fixed" in Appendix F): capture_cop=20, capture_thief=5,
survival_cop=5, survival_thief=10, tie_score=2, technical_loss=0.
"""

from __future__ import annotations

from dataclasses import dataclass

from police_thief.domain.rules import GameOutcome


@dataclass(frozen=True)
class ScoreResult:
    cop_score: int
    thief_score: int


def score_outcome(outcome: GameOutcome, scoring_config: dict) -> ScoreResult:
    """Look up the asymmetric payoff for `outcome` in `scoring_config`
    (the "scoring" section of config/game.json: capture_cop, capture_thief,
    survival_cop, survival_thief, technical_loss)."""
    if outcome == GameOutcome.CAPTURE:
        return ScoreResult(
            cop_score=scoring_config["capture_cop"],
            thief_score=scoring_config["capture_thief"],
        )
    if outcome == GameOutcome.SURVIVAL:
        return ScoreResult(
            cop_score=scoring_config["survival_cop"],
            thief_score=scoring_config["survival_thief"],
        )
    if outcome == GameOutcome.TECHNICAL_LOSS:
        loss = scoring_config["technical_loss"]
        return ScoreResult(cop_score=loss, thief_score=loss)
    raise ValueError(f"Unknown outcome: {outcome!r}")
