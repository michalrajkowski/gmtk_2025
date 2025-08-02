from __future__ import annotations
from typing import Optional

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import Which, Action
from game.objects.flag import Flag
from game.objects.locked_wall import LockedWall
from game.objects.toggle_switch import ToggleSwitch


class LevelSwitchLock(LevelBase):
    name: str = "Switch"
    difficulty: int = 1
    start_room: str = "A"
    max_cursors: int = 1
    loop_seconds: int = 10

    def __init__(self) -> None:
        # Positions (leave some space for your nav bar at y=0..16)
        self.switch = ToggleSwitch(x=40, y=60, w=16, h=16, is_on=False)
        self.wall = LockedWall(x=120, y=60, w=24, h=24, is_open=False)
        self.flag = Flag(x=120, y=60, w=24, h=24)

        # Wire switch → wall
        self.switch.on_toggle = self.wall.set_open
        # Mark completion when flag is clicked
        self.flag.on_finish = self._finish

    def _finish(self) -> None:
        self.completed = True

    # --- LevelBase ---
    def reset_level(self) -> None:
        self.completed = False
        self.switch.reset()
        self.wall.reset()
        self.flag.reset()

    def on_loop_start(self) -> None:
        # Keep state across loops (do nothing) OR reset per loop if you prefer.
        pass

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # 1) Switch always clickable
        self.switch.handle_input(which, action, x, y)

        # 2) If wall is closed and was clicked, it absorbs the click (blocks the flag)
        self.wall.handle_input(which, action, x, y)

        # 3) Flag only works when the wall is open (visible & clickable)
        if self.wall.is_open:
            self.flag.handle_input(which, action, x, y)

        return None

    def draw_room(self, room_id: str) -> None:
        self.switch.draw()
        if self.wall.is_open:
            self.flag.draw()
        else:
            self.wall.draw()
