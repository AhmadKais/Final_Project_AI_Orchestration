"""GamePhaseMachine: legal transitions succeed, illegal ones raise."""

import pytest

from police_thief.peer_runtime.state_machine import GamePhaseMachine


def test_legal_transition_updates_state():
    m = GamePhaseMachine()
    assert m.transition("COMPUTING_MOVE") == "COMPUTING_MOVE"


def test_illegal_transition_raises():
    m = GamePhaseMachine()
    with pytest.raises(ValueError):
        m.transition("VERIFYING")


def test_technical_loss_is_terminal():
    m = GamePhaseMachine()
    m.transition("COMPUTING_MOVE")
    m.transition("TECHNICAL_LOSS")
    with pytest.raises(ValueError):
        m.transition("WAITING_FOR_OPPONENT")
