"""Live per-peer window: belief heatmap + turn-status banner (Sec. 7.3, Fig. 9).

Heatmap: this agent's belief map about the hidden opponent, deeper red =
higher probability. Turn banner: green "YOUR TURN" when the opponent has
handed control back; gray "LOCKED" once a Commit has been sent.
"""

from __future__ import annotations

from police_thief.domain.belief import BeliefMap

_NO_BELIEF_COLOR = (255, 255, 255)  # white
_PEAK_BELIEF_COLOR = (200, 0, 0)  # deep red


def heatmap_color(probability: float, max_probability: float) -> str:
    """Map a belief-map probability to a hex color, white (no belief) to
    deep red (high belief), scaled relative to the map's current peak so
    the display stays readable at any grid size (Sec. 7.3.1)."""
    ratio = 0.0 if max_probability <= 0 else max(0.0, min(1.0, probability / max_probability))
    r, g, b = (
        round(lo + (hi - lo) * ratio)
        for lo, hi in zip(_NO_BELIEF_COLOR, _PEAK_BELIEF_COLOR)
    )
    return f"#{r:02x}{g:02x}{b:02x}"


def banner_state(is_my_turn: bool) -> tuple[str, str]:
    """(text, color) for the turn-status banner (Sec. 7.3.2): green "YOUR
    TURN" once control is handed back, gray "LOCKED" after a Commit is sent."""
    return ("YOUR TURN", "#2ecc71") if is_my_turn else ("LOCKED", "#95a5a6")


class LiveGUI:
    """Tkinter belief-heatmap + turn-banner window (Fig. 9). Local truth
    only -- this ever renders this agent's own belief map, never the
    objective board (Appendix E rules 8-9).

    Requires a display and the `tkinter` stdlib module (Debian/Ubuntu:
    `sudo apt install python3-tk`), so the widget-building code below is
    not exercised by the test suite -- only the pure `heatmap_color`/
    `banner_state` logic above is, which is what actually determines what
    gets drawn.
    """

    _CELL_PX = 40

    def __init__(self, role: str):
        self.role = role
        self._root = None
        self._canvas = None
        self._banner_label = None

    def _ensure_root(self) -> None:
        import tkinter as tk

        if self._root is not None:
            return
        self._root = tk.Tk()
        self._root.title(f"{self.role} -- Local Truth")
        self._banner_label = tk.Label(self._root, text="", font=("Helvetica", 16, "bold"))
        self._banner_label.pack(side="bottom", fill="x")

    def render_heatmap(self, belief: BeliefMap) -> None:
        import tkinter as tk

        self._ensure_root()
        size_px = belief.grid_size * self._CELL_PX
        if self._canvas is None:
            self._canvas = tk.Canvas(self._root, width=size_px, height=size_px)
            self._canvas.pack(side="top")

        max_p = max(belief.probabilities.values(), default=0.0)
        self._canvas.delete("all")
        for (row, col), prob in belief.probabilities.items():
            color = heatmap_color(prob, max_p)
            x0, y0 = col * self._CELL_PX, row * self._CELL_PX
            self._canvas.create_rectangle(
                x0, y0, x0 + self._CELL_PX, y0 + self._CELL_PX, fill=color, outline="black"
            )
        self._root.update_idletasks()

    def set_turn_banner(self, is_my_turn: bool) -> None:
        self._ensure_root()
        text, color = banner_state(is_my_turn)
        self._banner_label.config(text=text, background=color)
        self._root.update_idletasks()
