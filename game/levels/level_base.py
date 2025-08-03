from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Any

from game.core.cursor import CursorEvent
from game.objects.base import Which, Action


class LevelBase(ABC):
    name: str = "Level"
    difficulty: int = 1
    start_room: str = "A"
    completed: bool = False
    max_cursors: int = 10
    loop_seconds: int = 10

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

    def set_active_actor(self, actor_id: int) -> None:
        """Called just before interact() for a given actor (player=-1, ghosts=0..)."""
        self._active_actor_id = actor_id  # type: ignore[attr-defined]

    def on_actor_frame(self, actor_id: int, x: int, y: int, room_id: str) -> None:
        """Called every frame for every actor with its effective position & room."""
        return None

    def draw_room_overlay(self, room_id: str) -> None:
        """Draw extra elements that should appear above everything else (e.g., carried items)."""
        return None

    def seed_timelines(self, tm: Any) -> None:
        return None

    def set_loops_left_provider(self, provider):  # type: ignore[no-redef]
        """GameplayScene calls this with a callable returning remaining loops (including current)."""
        return None
