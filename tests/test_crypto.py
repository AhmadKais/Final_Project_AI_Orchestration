"""Commit-Reveal: commit()/verify() round-trip and tamper detection."""

import pytest


@pytest.mark.skip(reason="Stage 6 (Security and Cryptography) not yet implemented -- see docs/PRD/06-security-and-cryptography.md")
def test_verify_accepts_matching_reveal():
    ...


@pytest.mark.skip(reason="Stage 6 (Security and Cryptography) not yet implemented -- see docs/PRD/06-security-and-cryptography.md")
def test_verify_rejects_tampered_move():
    ...
