from __future__ import annotations
from typing import Optional, List

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import Which, Action
from game.objects.flag import Flag
from game.objects.locked_wall import LockedWall
from game.objects.button import Button

import pyxel


class LevelFourHoldLock(LevelBase):
    name: str = "4-Hold Door"
    difficulty: int = 1
    start_room: str = "A"
    max_cursors: int = 8
    loop_seconds: int = 20

    def __init__(self) -> None:
        # Leave room for nav (y >= ~20)
        self.buttons: List[Button] = [
            Button(x=40, y=64, w=0, h=0, radius=8),
            Button(x=70, y=64, w=0, h=0, radius=8),
            Button(x=40, y=104, w=0, h=0, radius=8),
            Button(x=70, y=104, w=0, h=0, radius=8),
        ]
        self.wall = LockedWall(x=150, y=80, w=24, h=24, is_open=False)
        self.flag = Flag(x=150, y=80, w=24, h=24)
        self.flag.on_finish = self._finish

    def _finish(self) -> None:
        self.completed = True

    # --- LevelBase ---
    def reset_level(self) -> None:
        self.completed = False
        for b in self.buttons:
            b.reset()
        self.wall.reset()
        self.flag.reset()

    def on_loop_start(self) -> None:
        # keep state across loops; per-frame hold will control the wall
        pass

    def _all_held(self) -> bool:
        return all(b.lit for b in self.buttons)

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # Update buttons first (Button.lit is true while held inside)
        for b in self.buttons:
            b.handle_input(which, action, x, y)

        # Open door only if all are held this frame
        self.wall.is_open = self._all_held()

        # Route click: wall blocks flag if closed
        if self.wall.is_open:
            self.flag.handle_input(which, action, x, y)
        else:
            self.wall.handle_input(which, action, x, y)

        return None

    def draw_room(self, room_id: str) -> None:
        # Ensure visuals match current state this frame
        self.wall.is_open = self._all_held()

        if self.wall.is_open:
            self.flag.draw()
        else:
            self.wall.draw()

        # Draw buttons last (note: Button.draw() resets .lit for next frame)
        for b in self.buttons:
            b.draw()

        pyxel.text(100, 20, "Press P to finish your loop quicker!", 7)
