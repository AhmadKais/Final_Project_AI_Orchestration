"""Bayesian belief map over the hidden opponent's location (Sec. 6.4).

b(s) = P(opponent = s | scent trail, verbal hints). Updated every turn by
cross-referencing the opponent's scent field against their (possibly false)
verbal hint -- a hint contradicted by the scent map is evidence of a lie
(Sec. 4.4's "Lie Detection" example), not proof the scent is wrong: the
scent trail is physically unforgeable.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from police_thief.domain.board import Coord
from police_thief.domain.scent import ScentField

# Deterministic keyword lexicon for parsing free-language hints into a
# spatial cue (Sec. 6.5's "language to the model, space to the algorithm"
# split: the LLM/template only produces text, this is the algorithmic side
# that turns it back into a belief-map update). (row_bias, col_bias): +1 =
# toward south/east edge, -1 = toward north/west edge.
_DIRECTION_KEYWORDS: dict[str, tuple[float, float]] = {
    "northeast": (-1, 1), "northwest": (-1, -1),
    "southeast": (1, 1), "southwest": (1, -1),
    "north": (-1, 0), "south": (1, 0),
    "east": (0, 1), "west": (0, -1),
}
_CENTER_KEYWORDS = ("center", "centre")


@dataclass
class BeliefMap:
    """A grid_size x grid_size posterior probability distribution."""

    grid_size: int
    probabilities: dict[Coord, float] = field(default_factory=dict)

    def _all_cells(self) -> list[Coord]:
        return [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]

    def _ensure_initialized(self) -> None:
        """Bootstrap a uniform prior on first use -- before any evidence
        arrives, every cell is equally likely."""
        if not self.probabilities:
            cells = self._all_cells()
            uniform = 1.0 / len(cells)
            self.probabilities = {cell: uniform for cell in cells}

    def _apply_likelihood(self, likelihood: dict[Coord, float]) -> None:
        """posterior(s) = prior(s) * likelihood(s), renormalized."""
        self._ensure_initialized()
        unnormalized = {
            cell: prob * likelihood.get(cell, 1.0)
            for cell, prob in self.probabilities.items()
        }
        total = sum(unnormalized.values())
        if total <= 0:
            # Degenerate case (evidence collapsed every cell to zero
            # likelihood): fall back to uniform rather than divide by zero.
            self.probabilities = {}
            self._ensure_initialized()
            return
        self.probabilities = {cell: value / total for cell, value in unnormalized.items()}

    def update_from_scent(self, opponent_scent: ScentField) -> None:
        """Bayesian update weighted by the opponent's (unforgeable) scent
        field: cells with fresh scent become more likely, cells with none
        stay at a neutral baseline (absence of scent is not proof of
        absence -- it may simply have decayed, Sec. 4.3)."""
        likelihood = {
            cell: 1.0 + opponent_scent.intensity_at(cell) for cell in self._all_cells()
        }
        self._apply_likelihood(likelihood)

    def update_from_hint(self, hint_text: str, trust_coefficient: float) -> None:
        """Bayesian update weighted by a parsed verbal hint. Recognizes
        cardinal/ordinal direction words and "center"/"centre" and biases
        the likelihood toward (or, for a hint the caller has flagged as
        distrusted via a negative `trust_coefficient`, away from) that
        region. An unrecognized hint carries no spatial information and
        leaves the belief unchanged, since a bluff need not even try to
        sound directional."""
        text = hint_text.lower()
        directions = [bias for keyword, bias in _DIRECTION_KEYWORDS.items() if keyword in text]
        mentions_center = any(keyword in text for keyword in _CENTER_KEYWORDS)
        if not directions and not mentions_center:
            return

        row_bias = sum(b[0] for b in directions) / len(directions) if directions else 0.0
        col_bias = sum(b[1] for b in directions) / len(directions) if directions else 0.0

        span = (self.grid_size - 1) or 1
        mid = span / 2

        likelihood: dict[Coord, float] = {}
        for cell in self._all_cells():
            row_align = (cell[0] - mid) / mid if mid else 0.0  # -1..1, + = south
            col_align = (cell[1] - mid) / mid if mid else 0.0  # -1..1, + = east
            factor = 1.0
            if directions:
                alignment = row_align * row_bias + col_align * col_bias  # -1..1
                factor *= max(0.05, 1.0 + trust_coefficient * alignment)
            if mentions_center:
                dist_from_mid = math.hypot(row_align, col_align) / math.sqrt(2)  # 0..1
                factor *= max(0.05, 1.0 + trust_coefficient * (1.0 - 2 * dist_from_mid))
            likelihood[cell] = factor
        self._apply_likelihood(likelihood)

    def arg_max(self) -> Coord:
        """The single most likely opponent cell, argmax_s b(s). Auto-
        initializes a uniform prior if no evidence has been observed yet
        (e.g. turn 0, before any scent/hint update) -- there is always
        SOME cell to aim for, even under total uncertainty."""
        self._ensure_initialized()
        return max(self.probabilities, key=self.probabilities.get)

    def manhattan_distance(self, frm: Coord, to: Coord) -> int:
        return abs(frm[0] - to[0]) + abs(frm[1] - to[1])
