"""Single business entry point (Appendix D): wires config -> Orchestrator ->
interface for one role, and exposes the replay/verification entry point.

This is the only module `__main__.py` should import from directly.
"""

from __future__ import annotations

import asyncio
import importlib
from pathlib import Path

from police_thief.domain.strategy.brain_base import BrainBase
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain
from police_thief.infra.llm.base import LLMProvider
from police_thief.infra.llm.claude_api_provider import ClaudeAPIProvider
from police_thief.infra.llm.claude_cli_provider import ClaudeCLIProvider
from police_thief.infra.llm.ollama_provider import OllamaProvider
from police_thief.infra.llm.template_provider import TemplateProvider
from police_thief.infra.mcp_client import OpponentClient
from police_thief.infra.mcp_server import MoveMailbox, build_server
from police_thief.interface.replay_viewer import ReplayViewer
from police_thief.peer_runtime.orchestrator import Orchestrator
from police_thief.shared.config_manager import Role, load_game_config

_PROVIDERS = {
    "template": TemplateProvider,
    "ollama": OllamaProvider,
    "claude_api": ClaudeAPIProvider,
    "claude_cli": ClaudeCLIProvider,
}


def _build_brain(role: Role, strategy_cfg: dict) -> BrainBase:
    """`[strategy] police_class`/`thief_class` points at `package.module:Class`
    (Appendix F Table 22); empty/absent runs the shipped HeuristicBrain."""
    class_path = strategy_cfg.get(f"{role}_class")
    if not class_path:
        return HeuristicBrain(role=role)
    module_path, _, class_name = class_path.partition(":")
    brain_cls = getattr(importlib.import_module(module_path), class_name)
    return brain_cls(role=role)


def _build_llm_provider(trash_talk_cfg: dict) -> LLMProvider:
    """`[trash_talk] provider` (Appendix F Table 21); defaults to the
    zero-token template provider."""
    provider_name = trash_talk_cfg.get("provider", "template")
    if provider_name not in _PROVIDERS:
        raise ValueError(f"Unknown trash_talk provider: {provider_name!r}")
    return _PROVIDERS[provider_name]()


def build_peer(role: Role, config_root: Path = Path("config")) -> Orchestrator:
    """Load config, construct the brain (from [strategy] or HeuristicBrain
    default), and assemble a ready-to-run Orchestrator for this role."""
    game_config = load_game_config(role, config_root)
    values = game_config.values
    network_cfg = values.get("network", {})

    brain = _build_brain(role, values.get("strategy", {}))
    llm_provider = _build_llm_provider(values.get("trash_talk", {}))

    mailbox = MoveMailbox()
    mcp_server = build_server(f"police_thief-{role}", mailbox)
    mcp_client = OpponentClient(
        network_cfg["opponent_url"],
        response_timeout_sec=values.get("network_and_league", {}).get("response_timeout_sec", 30),
    )

    orchestrator = Orchestrator(
        role=role, brain=brain, mcp_client=mcp_client, mailbox=mailbox,
        llm_provider=llm_provider, config=values,
        log_path=Path("logs") / f"{role}_match.json",
    )
    # Stashed for run_peer, which alone needs to bind the server; nothing
    # else in Orchestrator's own API depends on these.
    orchestrator._mcp_server = mcp_server
    orchestrator._my_port = network_cfg["my_port"]
    return orchestrator


async def _run_peer_async(orchestrator: Orchestrator) -> None:
    server_task = asyncio.create_task(
        orchestrator._mcp_server.run_async(transport="http", host="0.0.0.0", port=orchestrator._my_port)
    )
    await asyncio.sleep(0.5)  # let the server finish binding before the game loop starts
    try:
        outcome = await orchestrator.run_game()
        print(f"Game over: {outcome.value}")
    finally:
        server_task.cancel()


def run_peer(role: Role, config_root: Path = Path("config")) -> None:
    """Real network deployment: binds this role's server and runs the game
    loop against config/<role>/game.toml's [network] opponent_url. Needs a
    second real peer process to actually complete a game -- not something
    this repo's own test suite can exercise (see docs/TUNNELING.md's same
    caveat for Stage 5); the Orchestrator this builds is fully covered by
    tests/test_orchestrator_integration.py using an in-process transport.
    """
    orchestrator = build_peer(role, config_root)
    asyncio.run(_run_peer_async(orchestrator))


def run_replay(log_path: Path) -> None:
    """Launch the replay viewer against a saved game log for cryptographic
    re-verification (Sec. 7.4-7.5)."""
    ReplayViewer(log_path).step_through()
