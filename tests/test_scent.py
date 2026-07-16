"""Scent emission/decay formula: tau_ij(t+1) = max(0, (1-rho)*tau_ij(t) + delta_tau_ij)."""

from police_thief.domain.scent import ScentField


def test_emit_peaks_at_center():
    field = ScentField(grid_size=7)
    field.emit(center=(3, 3), peak=0.9, field_size=5)
    assert field.intensity_at((3, 3)) == 0.9


def test_emit_falls_off_with_distance():
    field = ScentField(grid_size=7)
    field.emit(center=(3, 3), peak=0.9, field_size=5)
    center = field.intensity_at((3, 3))
    ortho_neighbor = field.intensity_at((2, 3))
    diagonal_neighbor = field.intensity_at((2, 2))
    corner = field.intensity_at((1, 1))
    # Monotonic falloff with Euclidean distance from the emission center
    # (Sec. 4.3, Fig. 4): closer cells always carry more intensity.
    assert center > ortho_neighbor > diagonal_neighbor > corner > 0


def test_emit_roughly_matches_spec_figure_4_reference_values():
    # Fig. 4's worked example: center 0.90, ring-1 orthogonal 0.62,
    # ring-1 diagonal 0.42, ring-2 mid-edge 0.20. Our Gaussian falloff is
    # calibrated to the ring-1 point exactly; assert the others land close.
    field = ScentField(grid_size=7)
    field.emit(center=(3, 3), peak=0.9, field_size=5)
    assert field.intensity_at((3, 3)) == 0.9
    assert abs(field.intensity_at((2, 3)) - 0.62) < 1e-9
    assert abs(field.intensity_at((2, 2)) - 0.42) < 0.02
    assert abs(field.intensity_at((1, 3)) - 0.20) < 0.02


def test_emit_skips_cells_off_the_board():
    field = ScentField(grid_size=7)
    field.emit(center=(0, 0), peak=0.9, field_size=5)  # near the corner
    assert all(0 <= r < 7 and 0 <= c < 7 for (r, c) in field.intensities)


def test_emit_accumulates_across_multiple_deposits():
    field = ScentField(grid_size=7)
    field.emit(center=(3, 3), peak=0.9, field_size=5)
    first = field.intensity_at((3, 3))
    field.emit(center=(3, 3), peak=0.9, field_size=5)
    assert field.intensity_at((3, 3)) > first


def test_decay_reduces_intensity_by_rho():
    field = ScentField(grid_size=7, intensities={(3, 3): 0.9})
    field.decay(rho=0.10)
    assert field.intensity_at((3, 3)) == 0.9 * 0.90


def test_intensity_never_goes_negative():
    field = ScentField(grid_size=7, intensities={(3, 3): 0.01})
    for _ in range(50):
        field.decay(rho=0.10)
    assert field.intensity_at((3, 3)) >= 0.0


def test_intensity_at_absent_cell_is_zero():
    field = ScentField(grid_size=7)
    assert field.intensity_at((5, 5)) == 0.0


def test_full_turn_cycle_emit_then_decay():
    # A single deposit, then the six-turn "readable trail" behavior
    # described in Sec. 4.4 (Fig. 5): intensity should still be
    # meaningfully above zero a few turns after the agent has left.
    field = ScentField(grid_size=7)
    field.emit(center=(3, 3), peak=0.9, field_size=5)
    for _ in range(3):
        field.decay(rho=0.10)
    assert abs(field.intensity_at((3, 3)) - 0.9 * 0.9**3) < 1e-9
    assert field.intensity_at((3, 3)) > 0.5  # still a strong, readable trail
