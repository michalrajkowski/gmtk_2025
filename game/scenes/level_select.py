from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence, Tuple, Optional, Type, Callable

import pyxel
from game.levels.level_base import LevelBase


@dataclass(frozen=True)
class LevelEntry:
    factory: Type[LevelBase]  # class object (callable to instantiate)


class LevelSelectScene:
    def __init__(
        self,
        entries: Sequence[LevelEntry],
        start_level: Callable[
            [LevelBase], None
        ],  # <-- fix: function that starts a level instance
        draw_pointer: Callable[[int, int, int, int], None],
        width: int,
        height: int,
        is_completed: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self._entries = list(entries)
        self._start_level = start_level
        self._draw_pointer = draw_pointer
        self._w = width
        self._h = height
        self._is_completed = is_completed or (lambda _name: False)

        self._tile = 32
        self._gap = 20
        self._top = 24
        self._cols = 4

        total_w = self._cols * self._tile + (self._cols + 1) * self._gap
        self._left = max(0, (self._w - total_w) // 2)

    def _slot_rect(self, idx: int) -> Tuple[int, int, int, int]:
        col = idx % self._cols
        row = idx // self._cols
        x = self._left + self._gap + col * (self._tile + self._gap)
        row_step = self._tile + 24  # tile + text area
        y = self._top + row * row_step
        return x, y, self._tile, self._tile

    def _center_text(self, x: int, w: int, y: int, text: str, col: int) -> None:
        tw = len(text) * 4
        tx = x + (w - tw) // 2
        pyxel.text(tx, y, text, col)

    def _draw_difficulty_row(self, x: int, w: int, y: int, diff: int) -> None:
        # 0: gray gray gray; 1: green gray gray; 2: yellow yellow gray; 3+: red red red
        if diff <= 0:
            cols = [5, 5, 5]
        elif diff == 1:
            cols = [11, 5, 5]
        elif diff == 2:
            cols = [10, 10, 5]
        else:
            cols = [8, 8, 8]

        total_w = 20
        start_x = x + (w - total_w) // 2
        for i, col in enumerate(cols):
            px = start_x + i * 8  # 4px char + 4px space
            pyxel.text(px, y, "O", col)

    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            return

        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for i, entry in enumerate(self._entries):
                x, y, w, h = self._slot_rect(i)
                if x <= mx < x + w and y <= my < y + h:
                    # Instantiate the class and hand the instance to the starter
                    self._start_level(entry.factory())
                    return

    def draw(self) -> None:
        pyxel.cls(1)

        self._center_text(150, 10, 4, "T I M E    L O O P", 12)
        self._center_text(150, 10, 12, "SELECT YOUR LEVEL", 5)

        for i, entry in enumerate(self._entries):
            level_cls = entry.factory
            x, y, w, h = self._slot_rect(i)
            name = getattr(level_cls, "name", "Level")
            diff = int(getattr(level_cls, "difficulty", 0))
            done = self._is_completed(name)

            pyxel.rect(x, y, w, h, 11 if done else 0)
            pyxel.rectb(x, y, w, h, 7)

            self._center_text(x, w, y + h // 2 - 3, str(i + 1), 7)
            self._center_text(x, w, y + h + 6, f"{name}", 6)

            # <-- fix: pass the int 'diff' directly
            self._draw_difficulty_row(x, w, y + h + 12, diff)

        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))
        self._draw_pointer(int(mx), int(my), int(7), int(0))
