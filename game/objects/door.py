from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple

import pyxel
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which


@dataclass(slots=True)
class Door(LevelObject):
    x: int
    y: int
    w: int
    h: int
    target_room: str
    color: int = 9
    border: int = 7
    label: str = "Door"
    # Kept for compatibility but no longer used (we don't teleport on enter)
    spawn_at: Optional[Tuple[int, int]] = None
    on_enter: Optional[Callable[[str], None]] = None

    def reset(self) -> None:
        return None

    def handle_click(self, which: Which, px: int, py: int):
        if not self.contains(px, py):
            return None, None
        # Only change room; DO NOT teleport. Pointer stays exactly where it was.
        evt = CursorEvent(room=self.target_room, teleport_to=None)
        return None, evt

    def draw(self) -> None:
        pyxel.rect(self.x, self.y, self.w, self.h, self.color)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
        tw = len(self.label) * 4
        tx = self.x + (self.w - tw) // 2
        pyxel.text(tx, self.y - 8, self.label, 7)
