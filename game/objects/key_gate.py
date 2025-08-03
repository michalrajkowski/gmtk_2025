from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional

from game.objects.base import LevelObject, Which, Action
from game.objects.locked_wall import LockedWall


@dataclass(slots=True)
class KeyGate(LevelObject):
    x: int
    y: int
    w: int
    h: int
    required_key: int
    fill: int = 5
    border: int = 7
    icon_col: int = 7

    can_open: Optional[Callable[[int, int], bool]] = None
    _active_actor_id: Optional[int] = None

    _opened: bool = False
    _wall: LockedWall = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self._wall = LockedWall(
            x=self.x,
            y=self.y,
            w=self.w,
            h=self.h,
            is_open=False,
            fill=self.fill,
            border=self.border,
            icon_col=self.icon_col,
        )

    def reset(self) -> None:
        self._opened = False
        self._wall.is_open = False

    def set_active_actor(self, actor_id: int) -> None:
        self._active_actor_id = actor_id

    @property
    def is_open(self) -> bool:
        return self._opened

    def handle_input(self, which: Which, action: "Action", px: int, py: int):
        if self._opened:
            return None, None
        if action == "press" and self._wall.contains(px, py):
            if self.can_open and self._active_actor_id is not None:
                if self.can_open(self._active_actor_id, self.required_key):
                    self._opened = True
                    self._wall.is_open = True
            return None, None
        return None, None

    def draw(self) -> None:
        if not self._opened:
            self._wall.draw()
