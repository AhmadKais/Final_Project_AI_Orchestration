"""Scent emission/decay formula: tau_ij(t+1) = max(0, (1-rho)*tau_ij(t) + delta_tau_ij)."""

import pytest


@pytest.mark.skip(reason="Stage 4 (Language and Scent Integration) not yet implemented -- see docs/PRD/04-language-and-scent-integration.md")
def test_decay_reduces_intensity_by_rho():
    ...


@pytest.mark.skip(reason="Stage 4 (Language and Scent Integration) not yet implemented -- see docs/PRD/04-language-and-scent-integration.md")
def test_intensity_never_goes_negative():
    ...
