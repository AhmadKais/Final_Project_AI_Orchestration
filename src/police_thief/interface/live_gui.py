"""Live per-peer window: belief heatmap + turn-status banner (Sec. 7.3, Fig. 9).

Heatmap: this agent's belief map about the hidden opponent, deeper red =
higher probability. Turn banner: green "YOUR TURN" when the opponent has
handed control back; gray "LOCKED" once a Commit has been sent.
"""

from __future__ import annotations

from police_thief.domain.belief import BeliefMap


class LiveGUI:
    def __init__(self, role: str):
        self.role = role

    def render_heatmap(self, belief: BeliefMap) -> None:
        raise NotImplementedError

    def set_turn_banner(self, is_my_turn: bool) -> None:
        raise NotImplementedError
