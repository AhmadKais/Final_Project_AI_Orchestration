"""Stigmergy: decaying scent-trail emission and update (Sec. 4.2-4.4).

tau_ij(t+1) = max(0, (1 - rho) * tau_ij(t) + delta_tau_ij)

Each agent emits a radial scent field of size `pheromone_grid_size` (default
5x5) centered on itself every turn, peaking at `pheromone_center_intensity`
(0.9) and decaying at `pheromone_decay` (rho = 0.10) system-wide at the end
of every full turn. Each side reads only its *opponent's* scent field.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from police_thief.domain.board import Coord


@dataclass
class ScentField:
    """A grid_size x grid_size intensity map, tau, for one agent's trail."""

    grid_size: int
    intensities: dict[Coord, float] = field(default_factory=dict)

    def emit(self, center: Coord, peak: float, field_size: int) -> None:
        """Add a radial deposit of `peak` intensity centered on `center`,
        falling off with Manhattan/Chebyshev distance across `field_size`."""
        raise NotImplementedError

    def decay(self, rho: float) -> None:
        """Apply tau_ij(t+1) = max(0, (1-rho) * tau_ij(t)) to every cell."""
        raise NotImplementedError

    def intensity_at(self, cell: Coord) -> float:
        raise NotImplementedError
