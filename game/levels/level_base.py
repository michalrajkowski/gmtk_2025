from __future__ import annotations
from abc import ABC, abstractmethod


class LevelBase(ABC):
    # --- metadata ---
    name: str = "Level"
    difficulty: int = 1

    # --- lifecycle ---
    @abstractmethod
    def reset_level(self) -> None: ...
    @abstractmethod
    def on_loop_start(self) -> None: ...

    # --- input verbs ---
    @abstractmethod
    def handle_left_click(self, x: int, y: int) -> None: ...
    @abstractmethod
    def handle_right_click(self, x: int, y: int) -> None: ...

    # --- render ---
    @abstractmethod
    def draw(self) -> None: ...
