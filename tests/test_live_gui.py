"""Live GUI belief-heatmap + turn-banner logic (Sec. 7.3, Fig. 9).

Only the pure `heatmap_color`/`banner_state` helpers are tested here --
they're what actually determines what gets drawn. The `LiveGUI` class
itself needs a real display and the `tkinter` stdlib module, neither of
which is available in this headless environment; those widget-construction
tests are skipped gracefully rather than faked.
"""

import pytest

from police_thief.interface.live_gui import banner_state, heatmap_color


def test_heatmap_color_at_zero_probability_is_white():
    assert heatmap_color(0.0, max_probability=1.0) == "#ffffff"


def test_heatmap_color_at_peak_probability_is_deep_red():
    assert heatmap_color(1.0, max_probability=1.0) == "#c80000"


def test_heatmap_color_scales_with_relative_probability():
    low = heatmap_color(0.1, max_probability=1.0)
    high = heatmap_color(0.9, max_probability=1.0)
    assert low != high
    # Both should be valid 6-digit hex colors.
    assert len(low) == 7 and low.startswith("#")
    assert len(high) == 7 and high.startswith("#")


def test_heatmap_color_handles_zero_max_probability_without_crashing():
    assert heatmap_color(0.0, max_probability=0.0) == "#ffffff"


def test_banner_state_your_turn_is_green():
    text, color = banner_state(True)
    assert text == "YOUR TURN"
    assert color == "#2ecc71"


def test_banner_state_locked_is_gray():
    text, color = banner_state(False)
    assert text == "LOCKED"
    assert color == "#95a5a6"


def test_live_gui_widget_construction_requires_tkinter():
    tkinter = pytest.importorskip("tkinter")
    try:
        tkinter.Tk().destroy()
    except tkinter.TclError:
        pytest.skip("tkinter is importable but no display is available")

    from police_thief.domain.belief import BeliefMap
    from police_thief.interface.live_gui import LiveGUI

    gui = LiveGUI(role="police")
    gui.render_heatmap(BeliefMap(grid_size=3, probabilities={(0, 0): 0.5, (1, 1): 0.5}))
    gui.set_turn_banner(True)
