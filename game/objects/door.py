from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import pyxel
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class Door(LevelObject):
    x: int
    y: int
    w: int
    h: int
    target_room: str
    color: int = 9
    border: int = 7
    label: str = ""
    # 6×6 arrow sprite drawn with pset, centered on the door
    pattern: Tuple[str, str, str, str, str, str] = (
        "..##..",
        ".####.",
        "######",
        "..##..",
        "..##..",
        "..##..",
    )
    icon_col: int = 7
    # Spawn point kept for compat; we currently don't teleport on enter
    on_enter: Optional[Callable[[str], None]] = None

    def reset(self) -> None:
        return None

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if action != "press":
            return None, None
        if not self.contains(px, py):
            return None, None
        # Only change room; do not teleport pointer
        return None, CursorEvent(room=self.target_room, teleport_to=None)

    def draw(self) -> None:
        # Door body
        pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)

        # Centered arrow icon (pixel-by-pixel)
        ih = len(self.pattern)
        iw = len(self.pattern[0]) if ih > 0 else 0
        ox = self.x + (self.w - iw) // 2
        oy = self.y + (self.h - ih) // 2
        for j, row in enumerate(self.pattern):
            for i, ch in enumerate(row):
                if ch == "#":
                    pyxel.pset(ox + i, oy + j, self.icon_col)
