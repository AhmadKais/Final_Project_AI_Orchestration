"""One independent peer's runtime: negotiation -> turn loop -> audit (Appendix D).

The Orchestrator (single gateway, Sec. 8.3) wires together the state
machine, the MCP connector, the decision module (domain.strategy), the log
manager, the deadline tracker, and the watchdog (Fig. 12) -- no module
talks to another module directly.
"""
