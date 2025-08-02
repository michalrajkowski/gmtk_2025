from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional

from game.core.cursor import CursorEvent
from game.objects.base import Which, Action


class LevelBase(ABC):
    name: str = "Level"
    difficulty: int = 1
    start_room: str = "A"
    completed: bool = False  # set true by Flag

    @abstractmethod
    def reset_level(self) -> None: ...
    @abstractmethod
    def on_loop_start(self) -> None: ...

    # Per-cursor interaction in a specified room; may spawn objects internally.
    @abstractmethod
    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]: ...

    # Draw ONLY the given room
    @abstractmethod
    def draw_room(self, room_id: str) -> None: ...
