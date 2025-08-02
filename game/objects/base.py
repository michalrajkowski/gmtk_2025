from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Literal, Optional, Tuple

from game.core.cursor import CursorEvent

Which = Literal["L", "R"]
Action = Literal["press", "hold"]


class LevelObject(ABC):
    x: int
    y: int
    w: int
    h: int

    @abstractmethod
    def reset(self) -> None: ...

    # Returns: (spawned_object, cursor_event)
    def handle_input(
        self, which: Which, action: Action, px: int, py: int
    ) -> Tuple[Optional["LevelObject"], Optional[CursorEvent]]:
        return None, None

    @abstractmethod
    def draw(self) -> None: ...

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px < self.x + self.w and self.y <= py < self.y + self.h
