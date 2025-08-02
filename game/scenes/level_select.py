from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Sequence, Tuple, Optional

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
        is_completed: Optional[Callable[[str], bool]] = None,
    ) -> None:
        self._entries = list(entries)
        self._start_level = start_level
        self._draw_pointer = draw_pointer
        self._w = width
        self._h = height
        self._is_completed = is_completed or (lambda _name: False)

        self._tile = 32
        self._gap = 8
        self._top = 24

        total_w = len(self._entries) * self._tile + (len(self._entries) + 1) * self._gap
        self._left = max(0, (self._w - total_w) // 2)

    def _slot_rect(self, idx: int) -> Tuple[int, int, int, int]:
        x = self._left + self._gap + idx * (self._tile + self._gap)
        y = self._top
        return x, y, self._tile, self._tile

    def _center_text(self, x: int, w: int, y: int, text: str, col: int) -> None:
        tw = len(text) * 4
        tx = x + (w - tw) // 2
        pyxel.text(tx, y, text, col)

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
                    self._start_level(entry.factory())
                    return

    def draw(self) -> None:
        pyxel.cls(1)

        for i, entry in enumerate(self._entries):
            meta = entry.factory()
            x, y, w, h = self._slot_rect(i)
            done = self._is_completed(meta.name)

            pyxel.rect(x, y, w, h, 11 if done else 0)  # green if completed
            pyxel.rectb(x, y, w, h, 7)

            self._center_text(x, w, y + h // 2 - 3, str(i + 1), 7)
            label = f"{meta.name} ({meta.difficulty})"
            self._center_text(x, w, y + h + 6, label, 6)

        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))
        self._draw_pointer(int(mx), int(my), int(7), int(0))
