"""Outcome determination: capture-claim honesty, survival threshold, terminal state."""

import pytest

from police_thief.domain.rules import (
    GameOutcome,
    check_capture_claim,
    check_survival,
    determine_outcome,
)


def test_true_capture_claim_is_honest():
    assert check_capture_claim(True, cop_pos=(3, 3), thief_pos=(3, 3)) is True


def test_false_capture_claim_when_not_captured_is_dishonest():
    assert check_capture_claim(True, cop_pos=(0, 0), thief_pos=(3, 3)) is False


def test_false_denial_of_actual_capture_is_dishonest():
    assert check_capture_claim(False, cop_pos=(3, 3), thief_pos=(3, 3)) is False


def test_honest_non_capture_denial():
    assert check_capture_claim(False, cop_pos=(0, 0), thief_pos=(3, 3)) is True


def test_survival_below_threshold():
    assert check_survival(34, survival_threshold=35) is False


def test_survival_at_threshold():
    assert check_survival(35, survival_threshold=35) is True


def test_determine_outcome_forgery_takes_priority():
    outcome = determine_outcome(
        steps_taken=5, max_moves=35, captured=True,
        survival_threshold=35, forgery_detected=True,
    )
    assert outcome == GameOutcome.TECHNICAL_LOSS


def test_determine_outcome_capture():
    outcome = determine_outcome(
        steps_taken=5, max_moves=35, captured=True,
        survival_threshold=35, forgery_detected=False,
    )
    assert outcome == GameOutcome.CAPTURE


def test_determine_outcome_survival_by_threshold():
    outcome = determine_outcome(
        steps_taken=35, max_moves=35, captured=False,
        survival_threshold=35, forgery_detected=False,
    )
    assert outcome == GameOutcome.SURVIVAL


def test_determine_outcome_non_terminal_raises():
    with pytest.raises(ValueError):
        determine_outcome(
            steps_taken=1, max_moves=35, captured=False,
            survival_threshold=35, forgery_detected=False,
        )
