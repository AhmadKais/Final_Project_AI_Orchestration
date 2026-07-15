"""Win/loss/capture decision conditions (Sec. 3.5, Appendix E rules 21-22, 46-47).

- Capture: Cop lands on the Robber's cell (or barriers it) and declares a
  Capture Claim; the Robber is under cryptographic obligation to respond
  truthfully.
- Survival: Robber survives `survival_threshold` valid steps uncaptured.
- Technical loss: a side crashes, times out, or is caught in cryptographic
  forgery at audit -- scores 0 for both sides.
"""

from __future__ import annotations

from enum import Enum


class GameOutcome(str, Enum):
    CAPTURE = "capture"
    SURVIVAL = "survival"
    TECHNICAL_LOSS = "technical_loss"


def check_capture_claim(claimed: bool, cop_pos, thief_pos) -> bool:
    """True iff the Cop's Capture Claim matches reality (coordinate overlap).

    Enforces the "Duty of Truth in Capture" iron rule (Sec. 3.4): a claim
    that disagrees with the actual board state is a lie, whichever
    direction it lies in (falsely claiming a capture, or falsely denying
    one), and must be treated as a protocol violation upstream.
    """
    actual_capture = cop_pos == thief_pos
    return claimed == actual_capture


def check_survival(steps_survived: int, survival_threshold: int) -> bool:
    """True once the Robber has survived `survival_threshold` valid steps."""
    return steps_survived >= survival_threshold


def determine_outcome(*, steps_taken: int, max_moves: int, captured: bool,
                       survival_threshold: int, forgery_detected: bool) -> GameOutcome:
    """Map the current game state to one of the three terminal outcomes
    (Table 2). Raises if the state is not yet terminal -- callers should
    only invoke this once a turn's checks (capture/forgery/step-ceiling)
    have already established the game is over.
    """
    if forgery_detected:
        return GameOutcome.TECHNICAL_LOSS
    if captured:
        return GameOutcome.CAPTURE
    if steps_taken >= survival_threshold or steps_taken >= max_moves:
        return GameOutcome.SURVIVAL
    raise ValueError(
        "Game has not reached a terminal state "
        f"(steps_taken={steps_taken}, survival_threshold={survival_threshold}, "
        f"max_moves={max_moves})"
    )
