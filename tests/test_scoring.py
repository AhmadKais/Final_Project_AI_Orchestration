"""Scoring table payoffs (Table 2 / Appendix F Table 17 binding defaults)."""

import pytest

from police_thief.domain.rules import GameOutcome
from police_thief.domain.scoring import score_outcome

SCORING_CONFIG = {
    "capture_cop": 20,
    "capture_thief": 5,
    "survival_cop": 5,
    "survival_thief": 10,
    "tie_score": 2,
    "technical_loss": 0,
}


def test_capture_scores_favor_cop():
    result = score_outcome(GameOutcome.CAPTURE, SCORING_CONFIG)
    assert result.cop_score == 20
    assert result.thief_score == 5


def test_survival_scores_favor_thief():
    result = score_outcome(GameOutcome.SURVIVAL, SCORING_CONFIG)
    assert result.cop_score == 5
    assert result.thief_score == 10


def test_technical_loss_zeroes_both_sides():
    result = score_outcome(GameOutcome.TECHNICAL_LOSS, SCORING_CONFIG)
    assert result.cop_score == 0
    assert result.thief_score == 0


def test_unknown_outcome_raises():
    with pytest.raises(ValueError):
        score_outcome("not-a-real-outcome", SCORING_CONFIG)
