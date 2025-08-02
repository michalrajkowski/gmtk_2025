from __future__ import annotations
from typing import Final, List

from game.levels.level_base import LevelBase
from game.objects.click_pad import ClickPad


class LevelPads(LevelBase):
    """Four pads with thresholds 10, 20, 30, 100. Fully reset each loop."""

    PAD_W: Final[int] = 36
    PAD_H: Final[int] = 24
    GAP_X: Final[int] = 12
    GAP_Y: Final[int] = 12

    def __init__(self) -> None:
        # Layout a simple 2x2 grid
        left = 8
        top = 20
        w = self.PAD_W
        h = self.PAD_H
        gx = self.GAP_X
        gy = self.GAP_Y

        self.pads: List[ClickPad] = [
            ClickPad(left, top, w, h, threshold=10, color=3),
            ClickPad(left + w + gx, top, w, h, threshold=20, color=4),
            ClickPad(left, top + h + gy, w, h, threshold=30, color=5),
            ClickPad(left + w + gx, top + h + gy, w, h, threshold=100, color=6),
        ]

    # --------- lifecycle ----------
    def reset_level(self) -> None:
        # Full wipe (used by N). Pads have no cross-loop persistence in this design,
        # so same as on_loop_start.
        for p in self.pads:
            p.reset()

    def on_loop_start(self) -> None:
        # Per requirement: completely reset on each new timeline
        for p in self.pads:
            p.reset()

    # --------- input verbs ----------
    def handle_left_click(self, x: int, y: int) -> None:
        for p in self.pads:
            p.handle_click("L", x, y)

    def handle_right_click(self, x: int, y: int) -> None:
        for p in self.pads:
            p.handle_click("R", x, y)

    # --------- render ----------
    def draw(self) -> None:
        # Optionally, draw a subtle title or frame decorations here (kept minimal)
        for p in self.pads:
            p.draw()
