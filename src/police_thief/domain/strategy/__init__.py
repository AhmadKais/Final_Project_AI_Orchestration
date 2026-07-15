"""The pluggable movement-policy ("brain") module (Chapter 6).

Three equal-value tracks for choosing a move: pure heuristics (Bayes +
Manhattan distance, the default), your own heuristic algorithm, or optional
reinforcement learning. The move decision is ALWAYS algorithmic -- the LLM
is only ever used for the verbal bluff layer (Sec. 6.5), never for spatial
reasoning, unless both teams explicitly agree otherwise (Sec. 6.5 exception).

Selected via config/<role>/game.toml's [strategy] section: `police_class` /
`thief_class` point at a `package.module:Class` that subclasses BrainBase.
Leaving it unset runs HeuristicBrain.
"""

from police_thief.domain.strategy.brain_base import BrainBase
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain

__all__ = ["BrainBase", "HeuristicBrain"]
