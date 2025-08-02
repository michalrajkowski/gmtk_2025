from __future__ import annotations
from dataclasses import dataclass

import pyxel
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class Button(LevelObject):
    # For consistency with rect base, we store x,y,w,h but treat as circle
    x: int
    y: int
    w: int
    h: int
    radius: int
    lit: bool = False
    color_off: int = 8  # red
    color_on: int = 11  # green
    border: int = 7

    def reset(self) -> None:
        self.lit = False  # not permanent

    def _contains_circle(self, px: int, py: int) -> bool:
        cx = self.x + self.radius
        cy = self.y + self.radius
        dx = px - cx
        dy = py - cy
        return dx * dx + dy * dy <= self.radius * self.radius

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        # lit while HELD inside
        if action == "hold" and self._contains_circle(px, py):
            self.lit = True
        return None, None

    def draw(self) -> None:
        cx = self.x + self.radius
        cy = self.y + self.radius
        pyxel.circ(cx, cy, self.radius, self.color_on if self.lit else self.color_off)
        pyxel.circb(cx, cy, self.radius, self.border)
        # reset lit for next frame (level will call interact again if held)
        self.lit = False
