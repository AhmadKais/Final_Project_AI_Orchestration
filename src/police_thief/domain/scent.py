"""Stigmergy: decaying scent-trail emission and update (Sec. 4.2-4.4).

tau_ij(t+1) = max(0, (1 - rho) * tau_ij(t) + delta_tau_ij)

Each agent emits a radial scent field of size `pheromone_grid_size` (default
5x5) centered on itself every turn, peaking at `pheromone_center_intensity`
(0.9) and decaying at `pheromone_decay` (rho = 0.10) system-wide at the end
of every full turn. Each side reads only its *opponent's* scent field.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from police_thief.domain.board import Coord

# Gaussian radial falloff shape constant, calibrated against spec Fig. 4's
# worked example (5x5 field, peak 0.9): at Euclidean distance 1 from the
# center the figure shows tau=0.62, i.e. exp(-k*1^2) = 0.62/0.90. The book
# gives no closed-form emission formula (only the temporal decay formula is
# binding, Sec. 4.3) -- this reproduces the figure's qualitative "smooth
# hill" shape closely: d=0 -> 0.90, d=1 -> 0.62, d=sqrt(2) -> 0.43,
# d=2 -> 0.20, d=2*sqrt(2) -> 0.05, matching the figure's ring values.
_RADIAL_FALLOFF_K = -math.log(0.62 / 0.90)


@dataclass
class ScentField:
    """A grid_size x grid_size intensity map, tau, for one agent's trail."""

    grid_size: int
    intensities: dict[Coord, float] = field(default_factory=dict)

    def _in_bounds(self, cell: Coord) -> bool:
        row, col = cell
        return 0 <= row < self.grid_size and 0 <= col < self.grid_size

    def emit(self, center: Coord, peak: float, field_size: int) -> None:
        """Add a radial deposit of `peak` intensity centered on `center`,
        falling off with Euclidean distance across `field_size` (Sec. 4.3,
        Fig. 4). Cells off the board are skipped -- scent only exists where
        the board does."""
        half = field_size // 2
        for d_row in range(-half, half + 1):
            for d_col in range(-half, half + 1):
                cell = (center[0] + d_row, center[1] + d_col)
                if not self._in_bounds(cell):
                    continue
                dist_sq = d_row * d_row + d_col * d_col
                delta = peak * math.exp(-_RADIAL_FALLOFF_K * dist_sq)
                self.intensities[cell] = self.intensities.get(cell, 0.0) + delta

    def decay(self, rho: float) -> None:
        """Apply tau_ij(t+1) = max(0, (1-rho) * tau_ij(t)) to every cell."""
        for cell, value in self.intensities.items():
            self.intensities[cell] = max(0.0, (1 - rho) * value)

    def intensity_at(self, cell: Coord) -> float:
        return self.intensities.get(cell, 0.0)
