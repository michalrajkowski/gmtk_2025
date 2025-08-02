from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import pyxel
from game.objects.base import LevelObject, Which, Action
from game.core.cursor import CursorEvent


@dataclass(slots=True)
class ToggleSwitch(LevelObject):
    x: int
    y: int
    w: int
    h: int
    is_on: bool = False
    color_on: int = 11  # green
    color_off: int = 8  # red
    border: int = 7
    on_toggle: Optional[Callable[[bool], None]] = None

    def reset(self) -> None:
        self.is_on = False

    def handle_input(
        self, which: Which, action: Action, px: int, py: int
    ) -> Tuple[Optional["LevelObject"], Optional[CursorEvent]]:
        if action != "press" or not self.contains(px, py):
            return None, None
        self.is_on = not self.is_on
        if self.on_toggle:
            self.on_toggle(self.is_on)
        return None, None

    def draw(self) -> None:
        fill = self.color_on if self.is_on else self.color_off
        pyxel.rect(self.x, self.y, self.w, self.h, fill)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
