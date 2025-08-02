from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from game.core.cursor import CursorEvent
from game.objects.base import Which


class LevelBase(ABC):
    name: str = "Level"
    difficulty: int = 1
    start_room: str = "A"  # default starting room id

    @abstractmethod
    def reset_level(self) -> None: ...
    @abstractmethod
    def on_loop_start(self) -> None: ...

    # Per-cursor interaction in a specified room; may spawn objects internally.
    @abstractmethod
    def interact(
        self, which: Which, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]: ...

    # Draw ONLY the given room
    @abstractmethod
    def draw_room(self, room_id: str) -> None: ...

    def handle_left_click(self, x: int, y: int) -> None:
        pass

    def handle_right_click(self, x: int, y: int) -> None:
        pass
