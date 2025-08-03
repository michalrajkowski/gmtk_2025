from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

import pyxel
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class KeyDoor(LevelObject):
    x: int
    y: int
    w: int
    h: int
    target_room: str
    required_key: int  # key_id needed
    color: int = 9  # door color (match key theme)
    border: int = 7
    icon_col: int = 7
    is_open: bool = False

    # callback supplied by the level to ask: does actor_id hold required_key?
    can_open: Optional[Callable[[int, int], bool]] = None
    # level supplies set_active_actor; we read it through a setter the level calls:
    _active_actor_id: Optional[int] = None  # set by level before interact

    def reset(self) -> None:
        self.is_open = False

    def set_active_actor(self, actor_id: int) -> None:
        self._active_actor_id = actor_id

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if not self.contains(px, py):
            return None, None

        # If closed, a press with the right key opens it
        if not self.is_open and action == "press":
            if self.can_open and self._active_actor_id is not None:
                if self.can_open(self._active_actor_id, self.required_key):
                    self.is_open = True

        # If open and pressed, change room
        if self.is_open and action == "press":
            return None, CursorEvent(room=self.target_room, teleport_to=None)

        return None, None

    def draw(self) -> None:
        pyxel.rect(
            self.x, self.y, self.w, self.h, self.color if not self.is_open else 1
        )
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)

        # small arrow icon (like your Door) centered
        pattern = (
            "..##..",
            ".####.",
            "######",
            "..##..",
            "..##..",
            "..##..",
        )
        ih = len(pattern)
        iw = len(pattern[0])
        ox = self.x + (self.w - iw) // 2
        oy = self.y + (self.h - ih) // 2
        col = self.icon_col if not self.is_open else 5
        for j, row in enumerate(pattern):
            for i, ch in enumerate(row):
                if ch == "#":
                    pyxel.pset(ox + i, oy + j, col)
