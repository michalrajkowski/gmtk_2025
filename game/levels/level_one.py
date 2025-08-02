from __future__ import annotations

from typing import Final, Literal

import pyxel

from game.levels.level_base import LevelBase


class LevelOne(LevelBase):
    """Debug level with a single clickable rectangle and counters."""

    RECT_W: Final[int] = 40
    RECT_H: Final[int] = 30

    def __init__(self) -> None:
        self.rect_x: int = 100
        self.rect_y: int = 40
        self.rect_w: int = self.RECT_W
        self.rect_h: int = self.RECT_H
        self.total_clicks: int = 0
        self.left_clicks: int = 0
        self.right_clicks: int = 0

    def reset_level(self) -> None:
        self.total_clicks = 0
        self.left_clicks = 0
        self.right_clicks = 0

    def on_loop_start(self) -> None:
        return None

    def _point_in_rect(self, x: int, y: int) -> bool:
        return (
            self.rect_x <= x < self.rect_x + self.rect_w
            and self.rect_y <= y < self.rect_y + self.rect_h
        )

    def _incr(self, which: Literal["L", "R"], x: int, y: int) -> None:
        if self._point_in_rect(x, y):
            self.total_clicks += 1
            if which == "L":
                self.left_clicks += 1
            else:
                self.right_clicks += 1

    def handle_left_click(self, x: int, y: int) -> None:
        self._incr("L", x, y)

    def handle_right_click(self, x: int, y: int) -> None:
        self._incr("R", x, y)

    def draw(self) -> None:
        # Clickable zone
        pyxel.rect(self.rect_x, self.rect_y, self.rect_w, self.rect_h, 3)
        pyxel.rectb(self.rect_x, self.rect_y, self.rect_w, self.rect_h, 7)

        # Labels
        label_x: int = self.rect_x + 2
        label_y: int = self.rect_y - 8
        pyxel.text(label_x, label_y, f"Clicks: {self.total_clicks}", 7)
        pyxel.text(
            label_x, label_y - 8, f"L:{self.left_clicks}  R:{self.right_clicks}", 5
        )
        pyxel.text(label_x, label_y - 16, "Use mouse: L/R click", 5)
