from __future__ import annotations
from typing import Optional

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import Which, Action
from game.objects.button import Button
from game.objects.locked_wall import LockedWall
from game.objects.flag import Flag
from game.objects.door import Door


class LevelFirstRoomButton(LevelBase):
    name: str = "A... Door?"
    difficulty: int = 1
    start_room: str = "A"
    max_cursors: int = 3
    loop_seconds: int = 10

    def __init__(self) -> None:
        # --- Room A layout (leave space for nav at y>=16) ---
        # Left: Button A (hold) -> opens left wall -> reveals Door to room B
        self.button_a = Button(x=34, y=104, w=0, h=0, radius=9)
        self.wall_left = LockedWall(x=34, y=64, w=24, h=24, is_open=False)
        self.door_left = Door(x=34, y=64, w=24, h=24, target_room="B")

        # Right: wall covers Flag; opened by Button B in room B
        self.wall_right = LockedWall(x=140, y=64, w=24, h=24, is_open=False)
        self.flag_right = Flag(x=140, y=64, w=24, h=24)
        self.flag_right.on_finish = self._finish

        # --- Room B layout ---
        # Only Button B (hold) -> opens right wall in room A
        self.button_b = Button(x=64, y=96, w=0, h=0, radius=10)

    def _finish(self) -> None:
        self.completed = True

    # Optional: per-frame prep so hold states are frame-accurate across rooms
    def begin_frame(self) -> None:
        # Clear 'lit' so any hold this frame must set it again via interact()
        self.button_a.lit = False
        self.button_b.lit = False

    # --- LevelBase ---
    def reset_level(self) -> None:
        self.completed = False
        self.wall_left.reset()
        self.wall_right.reset()
        self.flag_right.reset()
        self.button_a.reset()
        self.button_b.reset()

    def on_loop_start(self) -> None:
        # Persist walls as closed at the start of each loop
        self.wall_left.is_open = False
        self.wall_right.is_open = False

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # Room A logic
        if room_id == "A":
            # Update Button A
            self.button_a.handle_input(which, action, x, y)
            # Left wall follows button A hold
            self.wall_left.is_open = self.button_a.lit

            # If open, the Door Left can be clicked to enter room B
            if self.wall_left.is_open:
                spawned, evt = self.door_left.handle_input(which, action, x, y)
                if evt is not None:
                    return evt

            # Right side: opened by Button B (from room B) this frame
            # (button_b.lit is set by room B interactions)
            self.wall_right.is_open = self.button_b.lit
            if self.wall_right.is_open:
                self.flag_right.handle_input(which, action, x, y)
            else:
                self.wall_right.handle_input(which, action, x, y)

            return None

        # Room B logic
        if room_id == "B":
            # Button B controls right wall in Room A
            self.button_b.handle_input(which, action, x, y)
            return None

        return None

    def draw_room(self, room_id: str) -> None:
        if room_id == "A":
            # Left: wall or door depending on current button A hold
            if self.button_a.lit:
                self.door_left.draw()
            else:
                self.wall_left.draw()

            # Right: wall or flag depending on button B hold (cross-room)
            if self.button_b.lit:
                self.flag_right.draw()
            else:
                self.wall_right.draw()

            self.button_a.draw()  # sets button_a.lit = False for next frame

        elif room_id == "B":
            self.button_b.draw()  # sets button_b.lit = False for next frame
