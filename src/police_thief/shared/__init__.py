"""Cross-cutting utilities shared by both peers: config loading, rate
limiting, system/hardware info for Step-0, and versioning.

Nothing in this package may hold live game state -- see the mandatory
process-separation rule (spec Sec. 2.4.2 / Appendix E, rule 2).
"""
