"""Statistical strategy evaluation: does MinimaxBrain actually play a
*better* game than a no-lookahead greedy policy, across many randomized
matchups -- not just "does it not crash on one hand-picked board" (that's
`test_strategy.py`'s job). Runs full local games (tests/support/local_sim.py)
against three opponent archetypes:

  - RandomBrain -- rock-bottom baseline; MinimaxBrain should win almost every game.
  - GreedyBrain -- reproduces the lecturer-provided reference simulator's
    shipped baseline (one-ply distance-to-belief-peak, no lookahead) -- a
    realistic opponent, since that repo is an explicitly-endorsed starting
    point for other students.
  - HeuristicBrain -- this project's own pre-search baseline, to prove the
    minimax upgrade is a genuine improvement and not a lateral move.

Trials randomize start positions (seeded, so failures are reproducible) --
fixed start positions would replay the exact same deterministic game every
time and prove nothing statistically.
"""

from __future__ import annotations

import random

import pytest

from police_thief.domain.board import Coord
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain
from police_thief.domain.strategy.minimax_brain import MinimaxBrain
from tests.support.local_sim import GRID_SIZE, GameResult, GreedyBrain, RandomBrain, play_game

_MIN_START_DISTANCE = 3


def _random_start_positions(rng: random.Random, grid_size: int = GRID_SIZE) -> tuple[Coord, Coord]:
    cells = [(r, c) for r in range(grid_size) for c in range(grid_size)]
    while True:
        cop = rng.choice(cells)
        thief = rng.choice(cells)
        if abs(cop[0] - thief[0]) + abs(cop[1] - thief[1]) >= _MIN_START_DISTANCE:
            return cop, thief


def _win_rate(results: list[GameResult], winner: str) -> float:
    return sum(1 for r in results if r.winner == winner) / len(results)


def _run_trials(make_police, make_thief, n: int, seed: int, fixed_start: tuple[Coord, Coord] | None = None) -> list[GameResult]:
    results = []
    for i in range(n):
        if fixed_start is not None:
            cop_start, thief_start = fixed_start
        else:
            cop_start, thief_start = _random_start_positions(random.Random(f"{seed}:{i}:pos"))
        # Independent per-role RNGs, NOT one shared instance: MinimaxBrain's
        # tie-break jitter must actually differ between the two sides for a
        # mirror matchup to mean anything (see minimax_brain.py's docstring
        # on why two byte-identical, perfectly-correlated searches can lock
        # into a standoff). A shared RNG would make the two "independent"
        # jitters secretly correlated too, undermining the exact thing being
        # relied on.
        police = make_police(random.Random(f"{seed}:{i}:police"))
        thief = make_thief(random.Random(f"{seed}:{i}:thief"))
        results.append(play_game(police, thief, cop_start=cop_start, thief_start=thief_start))
    return results


# -- vs. a rock-bottom random opponent: should win nearly every time -------

def test_minimax_police_dominates_random_thief():
    results = _run_trials(
        lambda rng: MinimaxBrain(role="police", rng=rng),
        lambda rng: RandomBrain(role="thief", rng=rng),
        n=30, seed=1,
    )
    # 0.85, not a stricter bound: partial observability means even against
    # a random Thief, a few turns of scent evidence are needed before
    # belief localizes it, and an occasional erratic run genuinely dodges
    # for a while within the 35-move limit -- measured consistently around
    # 85-88% across repeated independent samples, a comfortable floor.
    assert _win_rate(results, "police") >= 0.85


def test_minimax_thief_dominates_random_police():
    results = _run_trials(
        lambda rng: RandomBrain(role="police", rng=rng),
        lambda rng: MinimaxBrain(role="thief", rng=rng),
        n=30, seed=2,
    )
    assert _win_rate(results, "thief") >= 0.9


# -- vs. the reference simulator's own shipped baseline strategy -----------

def test_minimax_police_beats_greedy_thief_majority():
    results = _run_trials(
        lambda rng: MinimaxBrain(role="police", rng=rng),
        lambda rng: GreedyBrain(role="thief", rng=rng),
        n=30, seed=3,
    )
    assert _win_rate(results, "police") >= 0.6


def test_minimax_thief_beats_greedy_police_majority():
    results = _run_trials(
        lambda rng: GreedyBrain(role="police", rng=rng),
        lambda rng: MinimaxBrain(role="thief", rng=rng),
        n=30, seed=4,
    )
    assert _win_rate(results, "thief") >= 0.55


# -- the REAL match's fixed default start (config/game.json / Appendix F) --
# Every actual game starts here, not at a random pair of cells -- the
# randomized-start tests above are a good general signal, but this specific
# geometry deserves its own direct check since it's the one that will
# always be played for real (short of a negotiated change).

_REAL_COP_START: Coord = (0, 0)
_REAL_THIEF_START: Coord = (3, 3)


def test_minimax_police_dominates_random_thief_at_real_start():
    results = _run_trials(
        lambda rng: MinimaxBrain(role="police", rng=rng),
        lambda rng: RandomBrain(role="thief", rng=rng),
        n=20, seed=7, fixed_start=(_REAL_COP_START, _REAL_THIEF_START),
    )
    assert _win_rate(results, "police") >= 0.85


def test_minimax_police_beats_greedy_thief_at_real_start():
    results = _run_trials(
        lambda rng: MinimaxBrain(role="police", rng=rng),
        lambda rng: GreedyBrain(role="thief", rng=rng),
        n=20, seed=8, fixed_start=(_REAL_COP_START, _REAL_THIEF_START),
    )
    assert _win_rate(results, "police") >= 0.6


def test_minimax_thief_survives_greedy_police_at_real_start():
    results = _run_trials(
        lambda rng: GreedyBrain(role="police", rng=rng),
        lambda rng: MinimaxBrain(role="thief", rng=rng),
        n=20, seed=9, fixed_start=(_REAL_COP_START, _REAL_THIEF_START),
    )
    assert _win_rate(results, "thief") >= 0.5


# -- proves the search upgrade beats this project's own prior baseline -----

@pytest.mark.parametrize("role", ["police", "thief"])
def test_minimax_outperforms_or_matches_heuristic_vs_greedy(role):
    n, seed = 20, (5 if role == "police" else 6)
    opponent_role = "thief" if role == "police" else "police"

    def make_minimax(rng):
        return MinimaxBrain(role=role, rng=rng)

    def make_heuristic(rng):
        return HeuristicBrain(role=role)

    def make_greedy(rng):
        return GreedyBrain(role=opponent_role, rng=rng)

    if role == "police":
        minimax_results = _run_trials(make_minimax, make_greedy, n, seed)
        heuristic_results = _run_trials(make_heuristic, make_greedy, n, seed)
    else:
        minimax_results = _run_trials(make_greedy, make_minimax, n, seed)
        heuristic_results = _run_trials(make_greedy, make_heuristic, n, seed)

    minimax_rate = _win_rate(minimax_results, role)
    heuristic_rate = _win_rate(heuristic_results, role)
    assert minimax_rate >= heuristic_rate


# -- the hardest possible opponent: an identical copy of this same brain ---
#
# Two byte-identical MinimaxBrain instances compute perfectly correlated
# responses every turn. A live trace at the real default start showed this
# can lock into a stable adjacent-cell standoff that pure lookahead alone
# never resolves (confirmed non-monotonic by search depth, not a "just
# search deeper" problem) -- a known failure mode of deterministic
# pure-strategy play in symmetric simultaneous games. Independent
# per-instance tie-break jitter (minimax_brain._TIE_BREAK_JITTER) measurably
# improves the resolved rate but does not guarantee it every time, and
# nothing short of true mixed-strategy equilibrium play would. This test
# documents the REAL, measured floor rather than asserting a number that
# sounds reassuring -- a regression here means the jitter fix broke, not
# that the strategy stopped being strong against actual (non-identical)
# opponents, which the tests above already cover.

_MIRROR_MATCH_GEOMETRIES: list[tuple[Coord, Coord]] = [
    ((0, 0), (3, 3)),  # the real default start
    ((0, 0), (6, 6)),  # opposite corners
    ((3, 0), (3, 6)),  # axis-aligned, same row
    ((6, 0), (0, 6)),  # opposite corners, other diagonal
    ((2, 2), (4, 4)),  # closer together, off-center
]


def test_mirror_match_resolves_more_often_than_not():
    resolved = 0
    total = 0
    for cop_start, thief_start in _MIRROR_MATCH_GEOMETRIES:
        for trial in range(2):
            police = MinimaxBrain(role="police", rng=random.Random(f"mirror:{cop_start}:{trial}:police"))
            thief = MinimaxBrain(role="thief", rng=random.Random(f"mirror:{thief_start}:{trial}:thief"))
            result = play_game(police, thief, cop_start=cop_start, thief_start=thief_start)
            resolved += result.outcome != result.outcome.SURVIVAL
            total += 1
    # Documented floor, not a guarantee -- see the module comment above.
    assert resolved / total >= 0.5


# -- robustness: no illegal-move exceptions, every game terminates ---------

@pytest.mark.parametrize(
    "brain_pair",
    [
        (MinimaxBrain, MinimaxBrain),
        (MinimaxBrain, GreedyBrain),
        (MinimaxBrain, RandomBrain),
        (GreedyBrain, MinimaxBrain),
        (RandomBrain, MinimaxBrain),
    ],
)
def test_no_crashes_or_stalls_across_randomized_matchups(brain_pair):
    police_cls, thief_cls = brain_pair
    n = 8 if (police_cls is MinimaxBrain and thief_cls is MinimaxBrain) else 20
    for i in range(n):
        rng = random.Random(f"robustness:{police_cls.__name__}:{thief_cls.__name__}:{i}")
        cop_start, thief_start = _random_start_positions(rng)
        police = police_cls(role="police", rng=rng)
        thief = thief_cls(role="thief", rng=rng)
        result = play_game(police, thief, cop_start=cop_start, thief_start=thief_start)
        assert result.winner in ("police", "thief")
        assert result.steps_taken > 0
