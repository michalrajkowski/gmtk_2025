from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

import pyxel
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class Box(LevelObject):
    x: int
    y: int
    w: int
    h: int
    clicks_needed: int
    color: int = 3
    border: int = 7
    spawn_door_factory: Optional[Callable[[], LevelObject]] = None

    clicks: int = 0
    destroyed: bool = False

    def reset(self) -> None:
        self.clicks = 0
        self.destroyed = False

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if action != "press":
            return None, None
        if self.destroyed or not self.contains(px, py):
            return None, None
        self.clicks += 1
        if self.clicks >= self.clicks_needed:
            self.destroyed = True
            if self.spawn_door_factory is not None:
                return self.spawn_door_factory(), None
        return None, None

    def draw(self) -> None:
        if self.destroyed:
            pyxel.rect(self.x, self.y, self.w, self.h, 0)
            pyxel.rectb(self.x, self.y, self.w, self.h, 5)
            return
        pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
        rem = max(0, self.clicks_needed - self.clicks)
        txt = str(rem)
        tw = len(txt) * 4
        tx = self.x + (self.w - tw) // 2
        pyxel.text(tx, self.y - 8, txt, 7)
