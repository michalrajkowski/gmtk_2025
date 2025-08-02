from __future__ import annotations
from typing import Optional

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import Which, Action
from game.objects.flag import Flag
from game.objects.locked_wall import LockedWall
from game.objects.button import Button


class LevelButtonLock(LevelBase):
    name: str = "Hold Button!"
    difficulty: int = 1
    start_room: str = "A"
    max_cursors: int = 2
    loop_seconds: int = 10

    def __init__(self) -> None:
        # leave space for the top nav bar (y >= 24)
        self.button = Button(x=52, y=92, w=0, h=0, radius=10)  # hold to open
        self.wall = LockedWall(x=120, y=80, w=24, h=24, is_open=False)
        self.flag = Flag(x=120, y=80, w=24, h=24)

        # completion wiring
        self.flag.on_finish = self._finish

    def _finish(self) -> None:
        self.completed = True

    # --- LevelBase ---
    def reset_level(self) -> None:
        self.completed = False
        self.wall.reset()
        self.flag.reset()
        self.button.reset()

    def on_loop_start(self) -> None:
        # keep per-level state across loops (nothing special here)
        pass

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # 1) Update button (lit=True while held inside)
        self.button.handle_input(which, action, x, y)

        # 2) Open/close wall immediately based on current hold state
        self.wall.is_open = self.button.lit

        # 3) Route click: wall blocks flag when closed, otherwise flag is clickable
        if not self.wall.is_open:
            # absorbs clicks; returns nothing
            self.wall.handle_input(which, action, x, y)
        else:
            self.flag.handle_input(which, action, x, y)

        return None

    def draw_room(self, room_id: str) -> None:
        # Ensure visual matches current input state this frame
        self.wall.is_open = self.button.lit

        # Draw in this order so button.reset (inside draw) doesn't affect wall this frame
        if self.wall.is_open:
            self.flag.draw()
        else:
            self.wall.draw()

        self.button.draw()  # Button.draw() resets .lit to False for next frame
