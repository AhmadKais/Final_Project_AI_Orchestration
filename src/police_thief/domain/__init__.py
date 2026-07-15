"""Game-physics and decision domain: board, scent trails, belief maps,
movement/barrier rules, scoring, Commit-Reveal cryptography, wire protocol,
and the pluggable strategy ("brain") module.

Everything here is pure logic with no network or I/O -- both peers import
the exact same code so they compute the exact same physics (Sec. 3.2).
"""
