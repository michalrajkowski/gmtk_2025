from __future__ import annotations
from dataclasses import dataclass

import pyxel
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class Switch(LevelObject):
    x: int
    y: int
    w: int
    h: int
    flipped: bool = False
    color_off: int = 5  # gray
    color_on: int = 11  # bright green
    border: int = 7

    def reset(self) -> None:
        # permanent within the level session: do not reset on loop
        pass

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if action != "press":
            return None, None
        if not self.contains(px, py):
            return None, None
        self.flipped = True
        return None, None

    def draw(self) -> None:
        fill = self.color_on if self.flipped else self.color_off
        pyxel.rect(self.x, self.y, self.w, self.h, fill)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
