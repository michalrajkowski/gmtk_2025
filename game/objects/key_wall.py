# game/objects/key_wall.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional
import pyxel
from game.objects.base import LevelObject, Which, Action
from game.objects.locked_wall import LockedWall
from game.objects.door import Door


@dataclass(slots=True)
class KeyWall(LevelObject):
    x: int
    y: int
    w: int
    h: int
    target_room: str
    required_key: int
    wall_fill: int = 5
    wall_border: int = 7
    icon_col: int = 7
    spawn_door: bool = True

    can_open: Optional[Callable[[int, int], bool]] = None  # (actor_id, key_id) -> bool
    _active_actor_id: Optional[int] = None

    _wall: LockedWall = None  # type: ignore[assignment]
    _broken: bool = False

    def __post_init__(self) -> None:
        self._wall = LockedWall(
            x=self.x,
            y=self.y,
            w=self.w,
            h=self.h,
            is_open=False,
            fill=self.wall_fill,
            border=self.wall_border,
            icon_col=self.icon_col,
        )
        self._broken = False

    def reset(self) -> None:
        self._broken = False
        self._wall.is_open = False

    def set_active_actor(self, actor_id: int) -> None:
        self._active_actor_id = actor_id

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if not self._broken:
            if action == "press" and self._wall.contains(px, py):
                if self.can_open and self._active_actor_id is not None:
                    if self.can_open(self._active_actor_id, self.required_key):
                        self._broken = True
                        self._wall.is_open = True
                        if self.spawn_door:
                            door = Door(
                                x=self.x,
                                y=self.y,
                                w=self.w,
                                h=self.h,
                                target_room=self.target_room,
                                color=self.wall_fill,
                                border=self.wall_border,
                            )
                            return door, None
                        # same-room open: no spawn, just vanish visually
                        return None, None
                return None, None
            return None, None
        return None, None

    def draw(self) -> None:
        if not self._broken:
            self._wall.draw()
            return

        # Draw an “open passage” with a small arrow
        pyxel.rect(self.x, self.y, self.w, self.h, 1)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.wall_border)
        pattern = (
            "..##..",
            ".####.",
            "######",
            "..##..",
            "..##..",
            "..##..",
        )
        ih, iw = len(pattern), len(pattern[0])
        ox = self.x + (self.w - iw) // 2
        oy = self.y + (self.h - ih) // 2
        for j, row in enumerate(pattern):
            for i, ch in enumerate(row):
                if ch == "#":
                    pyxel.pset(ox + i, oy + j, self.icon_col)
