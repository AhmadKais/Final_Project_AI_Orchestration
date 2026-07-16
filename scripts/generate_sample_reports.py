"""Generate the four mandatory sample JSON reports (Sec. 9.3.3, Appendix F
Table 20) from an ACTUAL played match -- not fabricated data. Uses the same
in-process FastMCP transport as tests/test_orchestrator_integration.py, the
real shared config/game.json, and real Step-0 hardware declarations
(shared/system_info.py) for this machine.

Usage:
    uv run python scripts/generate_sample_reports.py

Writes into docs/sample_reports/ (committed, illustrative examples -- NOT
the same as the gitignored logs/ and reports/ directories, which hold real
per-match runtime artifacts).
"""

from __future__ import annotations

import asyncio
import json
import random
from pathlib import Path

from police_thief.domain.scoring import score_outcome
from police_thief.infra.llm.template_provider import TemplateProvider
from police_thief.infra.mcp_client import OpponentClient
from police_thief.infra.mcp_server import MoveMailbox, build_server
from police_thief.domain.strategy.heuristic_brain import HeuristicBrain
from police_thief.peer_runtime.orchestrator import Orchestrator
from police_thief.shared.config_manager import load_shared_config
from police_thief.shared.system_info import collect_step0_declaration, sign_declaration

GAME_UID = "demo-001"
SUB_GAME_NUMBER = "01"
OUT_DIR = Path(__file__).resolve().parent.parent / "docs" / "sample_reports"
CONFIG_ROOT = Path(__file__).resolve().parent.parent / "config"


async def play_sample_match() -> tuple[Orchestrator, Orchestrator]:
    police_mailbox, thief_mailbox = MoveMailbox(), MoveMailbox()
    police_mcp = build_server("police", police_mailbox)
    thief_mcp = build_server("thief", thief_mailbox)

    shared_config = load_shared_config(CONFIG_ROOT / "game.json")

    police = Orchestrator(
        role="police", brain=HeuristicBrain(role="police"),
        mcp_client=OpponentClient(thief_mcp, response_timeout_sec=5), mailbox=police_mailbox,
        llm_provider=TemplateProvider(rng=random.Random(1)), config=shared_config,
        log_path=OUT_DIR / f"log_{GAME_UID}_g{SUB_GAME_NUMBER}.json",
    )
    thief = Orchestrator(
        role="thief", brain=HeuristicBrain(role="thief"),
        mcp_client=OpponentClient(police_mcp, response_timeout_sec=5), mailbox=thief_mailbox,
        llm_provider=TemplateProvider(rng=random.Random(2)), config=shared_config,
        # No log_path: each side's log already contains BOTH roles' entries
        # (Orchestrator._write_log), so one canonical file per game
        # (police's) is the correct [Log File] per Table 20 -- writing a
        # second, near-identical copy under a made-up name would misrepresent
        # the file-naming convention this is meant to illustrate.
    )
    await asyncio.gather(police.run_game(), thief.run_game())
    return police, thief


def write_declaration(police: Orchestrator, thief: Orchestrator) -> None:
    """[Declaration File] (Appendix F Table 20): constant data for the
    whole game -- teams, repos, MCP addresses, hardware, LLM, token
    ceiling, timestamps (Sec. 9.3.3)."""
    police_decl = collect_step0_declaration(
        code_version="0.1.0", github_commit="0000000",
        group_name="sample-team-police", sub_game_number=1,
        llm_model="template",
    )
    thief_decl = collect_step0_declaration(
        code_version="0.1.0", github_commit="0000000",
        group_name="sample-team-thief", sub_game_number=1,
        llm_model="template",
    )
    signing_key = b"sample-signing-key-not-for-real-use"

    declaration = {
        "game_uid": GAME_UID,
        "teams": {
            "police": {
                "group_name": "sample-team-police", "group_id": "sample-police",
                "members": ["id-1001", "id-1002"],
                "repo": "https://github.com/example/police-repo",
            },
            "thief": {
                "group_name": "sample-team-thief", "group_id": "sample-thief",
                "members": ["id-2001", "id-2002"],
                "repo": "https://github.com/example/thief-repo",
            },
        },
        "mcp_addresses": {
            "police": "http://127.0.0.1:8801/mcp", "thief": "http://127.0.0.1:8802/mcp",
        },
        "hardware": {
            "police": {**vars(police_decl), "signature": sign_declaration(police_decl, signing_key)},
            "thief": {**vars(thief_decl), "signature": sign_declaration(thief_decl, signing_key)},
        },
        "token_budget_per_series": 200000,
    }
    (OUT_DIR / f"declaration_{GAME_UID}.json").write_text(json.dumps(declaration, indent=2))


def write_config() -> None:
    """[Configuration File] (Appendix F Table 20): the agreed, signed
    quantitative parameters -- the actual project config/game.json, so
    this sample is byte-identical to what both sides really loaded."""
    shared_config = load_shared_config(CONFIG_ROOT / "game.json")
    (OUT_DIR / f"config_{GAME_UID}_g{SUB_GAME_NUMBER}.json").write_text(
        json.dumps(shared_config, indent=2)
    )


def write_results(police: Orchestrator, thief: Orchestrator) -> None:
    """[Results File] (Appendix F Table 20): the final score summary sent
    to the instructor (Sec. 9.3.3) -- computed from the actual outcome."""
    scoring_config = load_shared_config(CONFIG_ROOT / "game.json")["scoring"]
    score = score_outcome(police.outcome, scoring_config)
    results = {
        "game_uid": GAME_UID,
        "sub_games": [
            {
                "sub_game_number": SUB_GAME_NUMBER,
                "outcome": police.outcome.value,
                "steps_taken": police.step,
                "cop_score": score.cop_score,
                "thief_score": score.thief_score,
                "forgery_detected": police.forgery_detected or thief.forgery_detected,
            }
        ],
        "cumulative": {"cop_score": score.cop_score, "thief_score": score.thief_score},
    }
    (OUT_DIR / f"result_{GAME_UID}.json").write_text(json.dumps(results, indent=2))


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    police, thief = asyncio.run(play_sample_match())
    write_declaration(police, thief)
    write_config()
    write_results(police, thief)
    print(f"Played a real match: outcome={police.outcome.value}, steps={police.step}")
    print(f"Wrote 4 sample report files to {OUT_DIR}/")


if __name__ == "__main__":
    main()
