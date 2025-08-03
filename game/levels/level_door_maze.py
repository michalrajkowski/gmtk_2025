from __future__ import annotations
from typing import Dict, List, Optional, Tuple

import pyxel

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action
from game.objects.door import Door
from game.objects.flag import Flag
from game.objects.box import Box


class LevelDoorMaze(LevelBase):
    """
    Room A: 4 doors -> 3 wrong send to trap rooms (single bottom door with down arrow,
             returns to start of A), 1 correct to Room B.
    Room B: same pattern -> 1 correct to Room C.
    Room C: same pattern -> 1 correct to F (final).
    Room F: Box(100 clicks) -> reveals Flag.
    """

    name: str = "Door Maze"
    difficulty: int = 2
    start_room: str = "A"
    max_cursors: int = 10
    loop_seconds: int = 10

    def __init__(self) -> None:
        # Where traps send the player back in Room A
        print("init!")
        self._start_spawn: Tuple[int, int] = (150, 160)  # screen center-ish under nav

        # Up-arrow (default Door.pattern) and a down-arrow (reversed)
        dummy = Door(x=0, y=0, w=0, h=0, target_room="A")
        self._up_pat = dummy.pattern
        self._down_pat = tuple(reversed(self._up_pat))

        self._chill_bank = 2
        self._chill_u, self._chill_v = 0, 0
        self._chill_w, self._chill_h = 128 * 2, 86 * 2  # <-- set to actual image size
        self._chill_x, self._chill_y = 10, 30  # where to draw in room "C_t2"

        pyxel.images[self._chill_bank].load(  # type: ignore
            self._chill_u, self._chill_v, "assets/chill_bill_small.png"
        )

        # Build rooms
        self._rooms: Dict[str, List[LevelObject]] = {}

        # --- Room A ---
        self._rooms["A"] = [
            # positions chosen to fit 300x200 canvas (nav ~16px high)
            Door(x=40, y=56, w=24, h=24, target_room="A_t1", color=9),  # wrong -> trap
            Door(x=136, y=28, w=24, h=24, target_room="A_t2", color=9),  # correct -> B
            Door(x=232, y=56, w=24, h=24, target_room="B", color=9),  # wrong -> trap
            Door(
                x=136, y=120, w=24, h=24, target_room="A_t3", color=9
            ),  # wrong -> trap
        ]
        # Trap rooms returning to A at _start_spawn (with DOWN arrow)
        self._rooms["A_t1"] = [  # pyright: ignore[reportArgumentType]
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]
        self._rooms["A_t2"] = [  # pyright: ignore[reportArgumentType]
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]
        self._rooms["A_t3"] = [  # pyright: ignore[reportArgumentType]
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]

        # --- Room B ---
        self._rooms["B"] = [
            Door(x=40, y=56, w=24, h=24, target_room="C", color=2),
            Door(x=136, y=28, w=24, h=24, target_room="B_t1", color=2),  # correct -> C
            Door(x=232, y=56, w=24, h=24, target_room="B_t2", color=2),
            Door(x=136, y=120, w=24, h=24, target_room="B_t3", color=2),
        ]
        self._rooms["B_t1"] = [  # pyright: ignore[reportArgumentType]
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]
        self._rooms["B_t2"] = [  # type: ignore
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]
        self._rooms["B_t3"] = [  # type: ignore
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]

        # --- Room C ---
        self._rooms["C"] = [
            Door(x=40, y=56, w=24, h=24, target_room="C_t1", color=12),
            Door(
                x=136, y=28, w=24, h=24, target_room="C_t2", color=12
            ),  # correct -> Final
            Door(x=232, y=56, w=24, h=24, target_room="F", color=12),
            Door(x=136, y=120, w=24, h=24, target_room="C_t3", color=12),
        ]
        self._rooms["C_t1"] = [  # type: ignore
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]
        self._rooms["C_t2"] = [  # type: ignore
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]
        self._rooms["C_t3"] = [  # type: ignore
            Door(
                x=136,
                y=140,
                w=24,
                h=24,
                target_room="A",
                pattern=self._down_pat,  # type: ignore
                color=1,
            )
        ]  # type: ignore[arg-type]

        # --- Final room F: Box → Flag ---
        self.box = Box(x=136, y=72, w=24, h=24, clicks_needed=100, color=3, border=7)
        self.flag = Flag(x=136, y=72, w=24, h=24)
        self.flag.on_finish = self._finish
        self._rooms["F"] = []  # drawn via custom logic below

    def _finish(self) -> None:
        self.completed = True

    # --- LevelBase API ---
    def reset_level(self) -> None:
        self.completed = False
        self.box.reset()
        self.flag.reset()

    def on_loop_start(self) -> None:
        # nothing special
        pass

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # Final room: box first, then flag becomes active when destroyed
        if room_id == "F":
            self.box.handle_input(which, action, x, y)
            if self.box.destroyed:
                self.flag.handle_input(which, action, x, y)
            return None

        # Other rooms: pass click to each object; return the first room change
        for obj in list(self._rooms.get(room_id, [])):
            spawned, evt = obj.handle_input(which, action, x, y)
            if spawned is not None:
                self._rooms[room_id].append(spawned)
            if evt is not None:
                return evt
        return None

    def draw_room(self, room_id: str) -> None:
        # set the color of current room flor:
        if room_id == "A":
            pyxel.cls(1)
        if room_id == "B" or room_id[:2] == "A_":
            pyxel.cls(9)
        if room_id == "C" or room_id[:2] == "B_":
            pyxel.cls(2)
        if room_id == "F" or room_id[:2] == "C_":
            pyxel.cls(12)

        if room_id == "C_t2":
            pyxel.blt(
                self._chill_x,
                self._chill_y,
                self._chill_bank,
                self._chill_u,
                self._chill_v,
                self._chill_w,
                self._chill_h,
                0,  # colkey: treat palette color 0 as transparent (adjust if needed)
            )

        if room_id == "F":
            # Draw box until destroyed; then draw flag
            if not self.box.destroyed:
                self.box.draw()
            else:
                self.flag.draw()
            return

        for obj in self._rooms.get(room_id, []):
            obj.draw()
