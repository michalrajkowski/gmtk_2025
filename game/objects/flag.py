from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

import pyxel
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class Flag(LevelObject):
    x: int
    y: int
    w: int
    h: int
    color: int = 10  # yellow/golden
    border: int = 7
    label: str = "click"
    on_finish: Optional[Callable[[], None]] = None

    def reset(self) -> None:
        pass

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if action != "press":
            return None, None
        if not self.contains(px, py):
            return None, None
        if self.on_finish:
            self.on_finish()
        return None, None

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
        tw = len(self.label) * 4
        tx = self.x + (self.w - tw) // 2
        pyxel.text(tx, self.y + 9, self.label, 7)
