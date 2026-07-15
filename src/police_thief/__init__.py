"""Distributed Cops-and-Robbers over a Peer-to-Peer Network.

Symmetric Cop/Robber agents communicating over FastMCP (Model Context
Protocol), with partial observability modeled as a Dec-POMDP, a decaying
scent-map belief mechanism, and a Commit-Reveal cryptographic fairness
protocol. See docs/PRD/ for the layered build order and police_thief_p2p_EN.md
for the full spec.
"""

from police_thief.shared.version import __version__

__all__ = ["__version__"]
