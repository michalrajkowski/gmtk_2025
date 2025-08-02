from __future__ import annotations
from typing import Optional

from game.levels.level_base import LevelBase
from game.objects.base import Which, Action
from game.core.cursor import CursorEvent
from game.objects.flag import Flag


class LevelFlagOnly(LevelBase):
    name: str = "Intro"
    difficulty: int = 0
    start_room: str = "A"
    max_cursors = 1

    def __init__(self) -> None:
        self._flag = Flag(x=120, y=80, w=24, h=24)
        # Wire completion callback
        self._flag.on_finish = self._mark_complete

    def _mark_complete(self) -> None:
        self.completed = True

    def reset_level(self) -> None:
        self.completed = False
        self._flag.reset()

    def on_loop_start(self) -> None:
        # Nothing to reset per loop
        pass

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        _, evt = self._flag.handle_input(which, action, x, y)
        return evt

    def draw_room(self, room_id: str) -> None:
        self._flag.draw()
