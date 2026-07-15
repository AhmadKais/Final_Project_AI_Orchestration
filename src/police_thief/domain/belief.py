"""Bayesian belief map over the hidden opponent's location (Sec. 6.4).

b(s) = P(opponent = s | scent trail, verbal hints). Updated every turn by
cross-referencing the opponent's scent field against their (possibly false)
verbal hint -- a hint contradicted by the scent map is evidence of a lie
(Sec. 4.4's "Lie Detection" example), not proof the scent is wrong: the
scent trail is physically unforgeable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from police_thief.domain.board import Coord
from police_thief.domain.scent import ScentField


@dataclass
class BeliefMap:
    """A grid_size x grid_size posterior probability distribution."""

    grid_size: int
    probabilities: dict[Coord, float] = field(default_factory=dict)

    def update_from_scent(self, opponent_scent: ScentField) -> None:
        """Bayesian update weighted by the opponent's (unforgeable) scent field."""
        raise NotImplementedError

    def update_from_hint(self, hint_text: str, trust_coefficient: float) -> None:
        """Bayesian update weighted by a parsed verbal hint, discounted by
        how much this hint has historically disagreed with scent evidence."""
        raise NotImplementedError

    def arg_max(self) -> Coord:
        """The single most likely opponent cell, argmax_s b(s)."""
        raise NotImplementedError

    def manhattan_distance(self, frm: Coord, to: Coord) -> int:
        raise NotImplementedError
