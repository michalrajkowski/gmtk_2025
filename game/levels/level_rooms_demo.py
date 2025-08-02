from __future__ import annotations
from typing import Dict, List, Optional


from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action
from game.objects.door import Door
from game.objects.box import Box
from game.objects.switch import Switch
from game.objects.button import Button


class LevelRoomsDemo(LevelBase):
    name: str = "MultiRoom"
    difficulty: int = 1
    start_room: str = "A"

    def __init__(self) -> None:
        self._rooms: Dict[str, List[LevelObject]] = {"A": [], "B": []}

        # Room A
        door_to_b = Door(
            x=120, y=30, w=24, h=24, target_room="B", color=4, label="To B"
        )

        def spawn_door_from_box() -> LevelObject:
            return Door(x=40, y=90, w=24, h=24, target_room="B", color=11, label="B!")

        box = Box(
            x=40,
            y=90,
            w=24,
            h=24,
            clicks_needed=10,
            color=3,
            spawn_door_factory=spawn_door_from_box,
        )
        sw = Switch(x=160, y=40, w=16, h=16)
        btn = Button(x=180, y=80, w=0, h=0, radius=8)
        self._rooms["A"] = [door_to_b, box, sw, btn]

        # Room B
        door_to_a = Door(x=40, y=30, w=24, h=24, target_room="A", color=6, label="To A")
        self._rooms["B"] = [door_to_a]

    def reset_level(self) -> None:
        # Reset permanent stuff only when the level is reloaded from the menu
        for objs in self._rooms.values():
            for obj in objs:
                obj.reset()
        self.completed = False

    def on_loop_start(self) -> None:
        # Keep switch state across loops (do not call reset here)
        pass

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        for obj in list(self._rooms.get(room_id, [])):
            spawned, evt = obj.handle_input(which, action, x, y)
            if spawned is not None:
                self._rooms[room_id].append(spawned)
            if evt is not None:
                return evt
        return None

    def draw_room(self, room_id: str) -> None:
        for obj in self._rooms.get(room_id, []):
            obj.draw()
