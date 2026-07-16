"""Reliability patterns: Deadline Tracker (per-request) and Watchdog
(whole-loop heartbeat) -- Sec. 8.4."""

import json
import time
from pathlib import Path

from police_thief.peer_runtime.deadline_tracker import DeadlineTracker
from police_thief.peer_runtime.watchdog import (
    _STATE_MARKER_PATH,
    HeartbeatWatchdog,
    controlled_shutdown,
    persist_state,
    watchdog_check,
)


def test_deadline_not_expired_immediately_after_start():
    tracker = DeadlineTracker(timeout_sec=1.0)
    tracker.start()
    assert tracker.is_expired() is False


def test_deadline_expires_after_timeout():
    tracker = DeadlineTracker(timeout_sec=0.01)
    tracker.start()
    time.sleep(0.02)
    assert tracker.is_expired() is True


def test_remaining_decreases_over_time():
    tracker = DeadlineTracker(timeout_sec=1.0)
    tracker.start()
    first = tracker.remaining()
    time.sleep(0.01)
    second = tracker.remaining()
    assert second < first


def test_remaining_never_goes_negative():
    tracker = DeadlineTracker(timeout_sec=0.01)
    tracker.start()
    time.sleep(0.05)
    assert tracker.remaining() == 0.0


def test_watchdog_alive_within_timeout():
    assert watchdog_check(last_heartbeat=time.time(), timeout_sec=180) == "ALIVE"


def test_watchdog_shutdown_after_timeout():
    # watchdog_check calls the module-level persist_state() with its default
    # path (logs/watchdog_state.json, relative to cwd) -- clean up the
    # marker it writes so the test has no lasting side effect.
    stale_heartbeat = time.time() - 200
    try:
        assert watchdog_check(last_heartbeat=stale_heartbeat, timeout_sec=180) == "SHUTDOWN"
    finally:
        Path(_STATE_MARKER_PATH).unlink(missing_ok=True)


def test_persist_state_writes_a_timestamped_marker(tmp_path):
    marker = tmp_path / "nested" / "watchdog_state.json"
    persist_state(marker)

    data = json.loads(marker.read_text())
    assert "frozen_at" in data
    assert data["frozen_at"] <= time.time()


def test_controlled_shutdown_is_a_safe_no_op():
    assert controlled_shutdown() is None


# -- HeartbeatWatchdog: real background-thread monitor (Sec. 8.4.2) --------

def test_heartbeat_watchdog_does_not_trigger_while_heartbeats_keep_coming():
    watchdog = HeartbeatWatchdog(timeout_sec=0.3, poll_interval_sec=0.05)
    watchdog.start()
    try:
        for _ in range(5):
            time.sleep(0.05)
            watchdog.heartbeat()
        assert watchdog.triggered.is_set() is False
    finally:
        watchdog.stop()
        Path(_STATE_MARKER_PATH).unlink(missing_ok=True)


def test_heartbeat_watchdog_triggers_when_heartbeats_stop():
    watchdog = HeartbeatWatchdog(timeout_sec=0.1, poll_interval_sec=0.05)
    watchdog.start()
    try:
        assert watchdog.triggered.wait(timeout=1.0) is True
    finally:
        watchdog.stop()
        Path(_STATE_MARKER_PATH).unlink(missing_ok=True)


def test_heartbeat_watchdog_stop_joins_the_thread():
    watchdog = HeartbeatWatchdog(timeout_sec=10, poll_interval_sec=0.05)
    watchdog.start()
    watchdog.stop()
    assert watchdog._thread.is_alive() is False
