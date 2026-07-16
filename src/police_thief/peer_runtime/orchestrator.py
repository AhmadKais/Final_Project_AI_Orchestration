"""Single-gateway Orchestrator (Sec. 8.3, Fig. 12).

Owns the GamePhaseMachine, the MCP connector (infra.mcp_client/mcp_server),
the decision module (domain.strategy.BrainBase), the log manager, and the
DeadlineTracker. No peripheral module talks to another directly --
everything is coordinated through this class.

Drives one peer's side of a full game: each turn runs the full Commit ->
Acknowledge -> Reveal -> Verify sequence (Sec. 5.3), advances this side's
local-truth Board with both sides' revealed moves, and updates the belief
map from the opponent's freshly-true position (scent) and hint. At game
end, exchanges Nonces for a mutual audit (Sec. 5.4) and writes a two-sided
game log a ReplayViewer can fully verify.

Cop barrier placement is wired in: HeuristicBrain.decide_barrier's choice
gets folded into the committed move string (domain.protocol.encode_move)
so it's cryptographically locked exactly like any other action, and
applied to the shared Board once both sides' reveals are in. Not wired in:
capture-claim honesty cross-checking via domain.rules.check_capture_claim
-- optional richness beyond what the underlying Commit-Reveal hash
verification already catches; the mechanic itself is unit-tested (Stage 1).
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from police_thief.domain.belief import BeliefMap
from police_thief.domain.board import Board, Coord, Move
from police_thief.domain.crypto import audit_log, commit
from police_thief.domain.protocol import decode_move, encode_move
from police_thief.domain.rules import GameOutcome, determine_outcome
from police_thief.domain.scent import ScentField
from police_thief.domain.strategy.brain_base import BrainBase
from police_thief.infra.llm.base import LLMProvider
from police_thief.infra.mcp_client import OpponentClient
from police_thief.infra.mcp_server import MoveMailbox
from police_thief.peer_runtime.deadline_tracker import DeadlineTracker
from police_thief.peer_runtime.state_machine import GamePhaseMachine

_OPPONENT_ROLE = {"police": "thief", "thief": "police"}


class Orchestrator:
    def __init__(
        self, *, role: str, brain: BrainBase, mcp_client: OpponentClient,
        mailbox: MoveMailbox, llm_provider: LLMProvider, config: dict,
        log_path: Path | None = None,
    ):
        self.role = role
        self.opponent_role = _OPPONENT_ROLE[role]
        self.brain = brain
        self.mcp_client = mcp_client
        self.mailbox = mailbox
        self.llm_provider = llm_provider
        self.config = config
        self.log_path = log_path

        board_cfg = config["board_and_agents"]
        move_cfg = config["movement_and_barriers"]
        pher_cfg = config["pheromones"]
        world_cfg = config.get("world", {})
        network_cfg = config.get("network_and_league", {})

        self.grid_size = board_cfg["grid_size"]
        self.max_moves = move_cfg["max_moves"]
        self.survival_threshold = move_cfg["survival_threshold"]
        self.pheromone_center_intensity = pher_cfg["pheromone_center_intensity"]
        self.pheromone_decay = pher_cfg["pheromone_decay"]
        self.pheromone_grid_size = pher_cfg["pheromone_grid_size"]
        self.hint_max_words = world_cfg.get("hint_max_words", 15)

        self.board = Board(
            grid_size=self.grid_size,
            cop_pos=tuple(board_cfg["cop_start"]),
            thief_pos=tuple(board_cfg["thief_start"]),
            max_barriers=move_cfg["max_barriers"],
        )
        self.belief = BeliefMap(grid_size=self.grid_size)
        self.opponent_scent = ScentField(grid_size=self.grid_size)

        self.phase = GamePhaseMachine()
        self.deadline = DeadlineTracker(timeout_sec=network_cfg.get("response_timeout_sec", 30))

        self.step = 0
        self.outcome: GameOutcome | None = None
        self.forgery_detected = False

        self._own_log: list[dict] = []
        self._opponent_h_commits: dict[int, str] = {}
        self._opponent_reveals: dict[int, dict] = {}
        self._opponent_pos_before_move: dict[int, Coord] = {}

    # -- local-truth helpers ----------------------------------------------

    def _own_pos(self) -> Coord:
        return self.board.cop_pos if self.role == "police" else self.board.thief_pos

    def _opponent_pos(self) -> Coord:
        return self.board.thief_pos if self.role == "police" else self.board.cop_pos

    def _canonical_state(self, role: str, step: int, pos: Coord) -> str:
        payload = {"role": role, "step": step, "pos": list(pos)}
        return json.dumps(payload, sort_keys=True, separators=(",", ":"))

    async def _await_with_deadline(self, queue: asyncio.Queue) -> dict | None:
        try:
            return await asyncio.wait_for(queue.get(), timeout=self.deadline.remaining() or 0.001)
        except asyncio.TimeoutError:
            return None

    def _technical_loss(self) -> bool:
        self.phase.transition("TECHNICAL_LOSS")
        self.outcome = GameOutcome.TECHNICAL_LOSS
        return False

    # -- one full turn ------------------------------------------------------

    async def run_turn(self) -> bool:
        """Drive one full turn through WAITING_FOR_OPPONENT -> ... ->
        VERIFYING. Returns True if the game continues, False if this turn
        ended it (capture, survival, or a technical loss)."""
        self.phase.transition("COMPUTING_MOVE")

        own_pos = self._own_pos()
        opponent_pos_before = self._opponent_pos()
        move = self.brain.pick_move(self.board, own_pos, self.belief)
        barrier_target = None
        if move == Move.STAY and self.role == "police":
            barrier_target = self.brain.decide_barrier(self.board, own_pos, self.belief)
        move_value = encode_move(move, barrier_target)
        hint = self.llm_provider.generate_hint(
            prompt=f"role={self.role} step={self.step}", word_limit=self.hint_max_words
        )
        intent = "true"
        state = self._canonical_state(self.role, self.step, own_pos)
        commitment = commit(state, move_value, intent)

        self.phase.transition("COMMITTING")
        self.deadline.start()
        await self.mcp_client.send_commit(role=self.role, step=self.step, h_commit=commitment.h_commit)
        opponent_commit = await self._await_with_deadline(self.mailbox.commits)
        if opponent_commit is None:
            return self._technical_loss()
        self._opponent_h_commits[self.step] = opponent_commit["h_commit"]
        self._opponent_pos_before_move[self.step] = opponent_pos_before

        self.deadline.start()
        await self.mcp_client.send_ack(role=self.role, step=self.step)
        opponent_ack = await self._await_with_deadline(self.mailbox.acks)
        if opponent_ack is None:
            return self._technical_loss()

        self.phase.transition("AWAITING_REVEAL")
        self.deadline.start()
        await self.mcp_client.send_reveal(role=self.role, step=self.step, move=move_value, hint=hint, intent=intent)
        opponent_reveal = await self._await_with_deadline(self.mailbox.reveals)
        if opponent_reveal is None:
            return self._technical_loss()
        self._opponent_reveals[self.step] = opponent_reveal

        self.phase.transition("VERIFYING")
        self._own_log.append({
            "step": self.step, "role": self.role, "state": state,
            "move": move_value, "intent": intent,
            "nonce": commitment.nonce, "h_commit": commitment.h_commit,
        })

        try:
            opponent_move, opponent_barrier_target = decode_move(opponent_reveal["move"])
            self.board.apply_move(self.role, move)
            self.board.apply_move(self.opponent_role, opponent_move)
            barrier_to_place = barrier_target or opponent_barrier_target
            if barrier_to_place is not None:
                # At most one side is ever the Cop, so at most one of the
                # two is non-None; STAY never moved cop_pos, so it's still
                # correct after both apply_move calls above.
                self.board.place_barrier(self.board.cop_pos, barrier_to_place)
        except ValueError:
            # The opponent revealed a move (or barrier) that is illegal
            # against the physics both sides are supposed to enforce
            # identically -- treat exactly like any other integrity failure.
            return self._technical_loss()

        if self.board.is_capture():
            claimed = self.role == "police"
            await self.mcp_client.send_capture_claim(role=self.role, claimed=claimed)
            await self._await_with_deadline(self.mailbox.capture_claims)
            self.outcome = determine_outcome(
                steps_taken=self.step + 1, max_moves=self.max_moves, captured=True,
                survival_threshold=self.survival_threshold, forgery_detected=False,
            )
            self.phase.transition("WAITING_FOR_OPPONENT")
            return False

        self.opponent_scent.emit(
            center=self._opponent_pos(), peak=self.pheromone_center_intensity,
            field_size=self.pheromone_grid_size,
        )
        self.opponent_scent.decay(self.pheromone_decay)
        self.belief.decay_toward_uniform(self.pheromone_decay)
        self.belief.update_from_scent(self.opponent_scent)
        self.belief.update_from_hint(opponent_reveal["hint"], trust_coefficient=1.0)

        self.step += 1
        if self.step >= self.max_moves or self.step >= self.survival_threshold:
            self.outcome = determine_outcome(
                steps_taken=self.step, max_moves=self.max_moves, captured=False,
                survival_threshold=self.survival_threshold, forgery_detected=False,
            )
            self.phase.transition("WAITING_FOR_OPPONENT")
            return False

        self.phase.transition("WAITING_FOR_OPPONENT")
        return True

    # -- end of game ----------------------------------------------------------

    async def run_game(self) -> GameOutcome:
        """Loop run_turn() until capture, survival, or technical loss, then
        run the mutual final audit and write the game log."""
        while await self.run_turn():
            pass

        if self.outcome != GameOutcome.TECHNICAL_LOSS:
            forged = await self._final_audit()
            if forged:
                self.outcome = GameOutcome.TECHNICAL_LOSS
                self.forgery_detected = True

        if self.log_path is not None:
            self._write_log()
        return self.outcome

    def _reconstruct_opponent_entries(self, opponent_nonces: list[str]) -> list[dict] | None:
        """Rebuild the opponent's (state, move, intent, nonce, h_commit)
        for every step from what was received live plus the position
        history this side independently tracked -- returns None if
        anything needed is missing (treated as forgery by the caller)."""
        entries = []
        for step, nonce in enumerate(opponent_nonces):
            reveal = self._opponent_reveals.get(step)
            h_commit = self._opponent_h_commits.get(step)
            pos_before = self._opponent_pos_before_move.get(step)
            if reveal is None or h_commit is None or pos_before is None:
                return None
            state = self._canonical_state(self.opponent_role, step, pos_before)
            entries.append({
                "step": step, "role": self.opponent_role, "state": state,
                "move": reveal["move"], "intent": reveal["intent"],
                "nonce": nonce, "h_commit": h_commit,
            })
        return entries

    async def _final_audit(self) -> bool:
        """Exchange all Nonces and re-verify every opponent commitment
        (Sec. 5.4). Returns True iff forgery was detected."""
        my_nonces = [entry["nonce"] for entry in self._own_log]
        await self.mcp_client.send_final_audit(role=self.role, nonces=my_nonces)
        opponent_audit = await self._await_with_deadline(self.mailbox.final_audits)
        if opponent_audit is None:
            return True

        entries = self._reconstruct_opponent_entries(opponent_audit["nonces"])
        if entries is None:
            return True
        self._opponent_verified_log = entries
        results = audit_log(entries)
        return any(not is_valid for _, is_valid in results)

    def _write_log(self) -> None:
        """Two-sided log: this side's own entries plus the opponent's
        reconstructed, audited entries -- a full match a ReplayViewer can
        verify end to end, not just one side's actions."""
        opponent_entries = getattr(self, "_opponent_verified_log", [])
        all_entries = sorted(self._own_log + opponent_entries, key=lambda e: (e["step"], e["role"]))
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self.log_path.write_text(json.dumps({"entries": all_entries}, indent=2))
