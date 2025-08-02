from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple

import pyxel
from game.levels.level_base import LevelBase


@dataclass(frozen=True)
class LevelEntry:
    factory: Callable[[], LevelBase]


class LevelSelectScene:
    def __init__(
        self,
        entries: Sequence[LevelEntry],
        start_level: Callable[[LevelBase], None],
        draw_pointer: Callable[[int, int, int, int], None],
        width: int,
        height: int,
    ) -> None:
        self._entries = list(entries)
        self._start_level = start_level
        self._draw_pointer = draw_pointer
        self._w = width
        self._h = height

        # Smaller tiles: fixed 32px squares with 8px gaps (2–3 columns)
        self._cols = 3 if width >= 240 else 2
        self._tile = 32
        self._gap = 8
        self._top = 16

    # ------------- helpers -------------
    def _grid_pos(self, idx: int) -> Tuple[int, int, int, int]:
        col = idx % self._cols
        row = idx // self._cols
        x = (self._gap + (self._tile + self._gap) * col) + self._gap
        y = self._top + (self._tile + 14 + self._gap) * row  # 14px label line
        return x, y, self._tile, self._tile

    def _center_text(self, x: int, w: int, y: int, text: str, col: int) -> None:
        tw = len(text) * 4
        tx = x + (w - tw) // 2
        pyxel.text(tx, y, text, col)

    # ------------- API -------------
    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            return

        # Clamp mouse to window for hit testing
        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i, entry in enumerate(self._entries):
                x, y, w, h = self._grid_pos(i)
                if x <= mx < x + w and y <= my < y + h:
                    self._start_level(entry.factory())
                    return

    def draw(self) -> None:
        pyxel.cls(1)  # background color 1

        for i, entry in enumerate(self._entries):
            meta = entry.factory()  # cheap: used to read name/difficulty
            x, y, w, h = self._grid_pos(i)

            # square
            pyxel.rect(x, y, w, h, 0)
            pyxel.rectb(x, y, w, h, 7)

            # big number
            num = str(i + 1)
            self._center_text(x, w, y + h // 2 - 3, num, 7)

            # name (and difficulty) centered below
            label = f"{meta.name} ({meta.difficulty})"
            self._center_text(x, w, y + h + 4, label, 6)

        # Draw custom mouse pointer on the menu
        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))
        self._draw_pointer(int(mx), int(my), int(7), int(0))
