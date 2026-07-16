"""Stage 4: Bayesian belief updates from scent fields and free-language hints."""

import pytest

from police_thief.domain.belief import BeliefMap
from police_thief.domain.scent import ScentField


def test_decay_toward_uniform_erodes_an_overconfident_stale_belief():
    # Reproduces a real bug found via full-game integration testing: a
    # belief that reached ~0.999 confidence at one cell took 10+ turns of
    # strong contradicting evidence to budge at all, because a pure
    # multiplicative Bayesian update only ever sharpens. decay_toward_uniform
    # must let fresh evidence actually win within a reasonable number of turns.
    belief = BeliefMap(grid_size=5)
    belief.probabilities = {(3, 3): 0.999}
    for cell in [(r, c) for r in range(5) for c in range(5)]:
        belief.probabilities.setdefault(cell, 0.0001 / 24)
    total = sum(belief.probabilities.values())
    belief.probabilities = {k: v / total for k, v in belief.probabilities.items()}

    scent = ScentField(grid_size=5)
    for _ in range(10):
        belief.decay_toward_uniform(0.10)
        scent.emit(center=(4, 4), peak=0.9, field_size=5)
        scent.decay(0.10)
        belief.update_from_scent(scent)

    assert belief.arg_max() == (4, 4)


def test_decay_toward_uniform_preserves_normalization():
    belief = BeliefMap(grid_size=5, probabilities={(2, 2): 0.7, (4, 4): 0.3})
    belief.decay_toward_uniform(0.2)
    assert abs(sum(belief.probabilities.values()) - 1.0) < 1e-9


def test_decay_toward_uniform_at_rate_one_is_fully_uniform():
    belief = BeliefMap(grid_size=5)
    belief.probabilities = {(r, c): 0.0 for r in range(5) for c in range(5)}
    belief.probabilities[(2, 2)] = 0.99
    belief.probabilities[(4, 4)] = 0.01

    belief.decay_toward_uniform(1.0)

    values = {round(v, 9) for v in belief.probabilities.values()}
    assert values == {round(1 / 25, 9)}


def test_probabilities_sum_to_one_after_scent_update():
    belief = BeliefMap(grid_size=5)
    scent = ScentField(grid_size=5)
    scent.emit(center=(2, 2), peak=0.9, field_size=5)

    belief.update_from_scent(scent)

    assert abs(sum(belief.probabilities.values()) - 1.0) < 1e-9


def test_scent_update_boosts_high_intensity_cells():
    belief = BeliefMap(grid_size=5)
    scent = ScentField(grid_size=5)
    scent.emit(center=(4, 4), peak=0.9, field_size=5)

    belief.update_from_scent(scent)

    assert belief.arg_max() == (4, 4)


def test_repeated_scent_updates_sharpen_belief():
    belief = BeliefMap(grid_size=5)
    scent = ScentField(grid_size=5)
    scent.emit(center=(1, 1), peak=0.9, field_size=5)

    belief.update_from_scent(scent)
    first_peak = belief.probabilities[(1, 1)]
    belief.update_from_scent(scent)
    second_peak = belief.probabilities[(1, 1)]

    assert second_peak > first_peak  # confirming evidence increases certainty


def test_hint_update_biases_toward_named_direction():
    belief = BeliefMap(grid_size=7)  # starts uniform on first update
    belief.update_from_hint("I saw them slip north near the gate", trust_coefficient=1.0)

    target = belief.arg_max()
    assert target[0] < 3  # north half of a top-left-origin, row-grows-downward board


def test_hint_update_biases_toward_south():
    belief = BeliefMap(grid_size=7)
    belief.update_from_hint("moving south along the river", trust_coefficient=1.0)

    target = belief.arg_max()
    assert target[0] > 3


def test_hint_update_biases_toward_center():
    belief = BeliefMap(grid_size=7)
    belief.update_from_hint("staying right in the center of the block", trust_coefficient=1.0)

    target = belief.arg_max()
    assert target == (3, 3)


def test_unrecognized_hint_leaves_belief_unchanged():
    belief = BeliefMap(grid_size=5, probabilities={(1, 1): 0.7, (3, 3): 0.3})
    before = dict(belief.probabilities)

    belief.update_from_hint("the weather is nice today", trust_coefficient=1.0)

    assert belief.probabilities == before


def test_negative_trust_coefficient_biases_away_from_claimed_direction():
    # Sec. 4.4's "Lie Detection": a hint contradicted by scent evidence
    # should be usable with a negative trust coefficient to bias AWAY from
    # the claimed direction once caught in a lie.
    belief = BeliefMap(grid_size=7)
    belief.update_from_hint("heading north", trust_coefficient=-1.0)

    target = belief.arg_max()
    assert target[0] > 3  # pushed toward south, away from the claimed north


def test_scent_and_hint_updates_compose():
    belief = BeliefMap(grid_size=7)
    scent = ScentField(grid_size=7)
    scent.emit(center=(5, 5), peak=0.9, field_size=5)

    belief.update_from_scent(scent)
    belief.update_from_hint("closing in from the south", trust_coefficient=1.0)

    assert abs(sum(belief.probabilities.values()) - 1.0) < 1e-9
    # Both pieces of evidence agree on the southeast quadrant; the hint's
    # directional pull can shift the exact peak (e.g. toward the board
    # edge), but the combined belief must stay concentrated near the scent.
    target = belief.arg_max()
    assert target[0] >= 4 and target[1] >= 4
