from __future__ import annotations

from abc import ABC, abstractmethod


class LevelBase(ABC):
    @abstractmethod
    def reset_level(self) -> None: ...
    @abstractmethod
    def on_loop_start(self) -> None: ...

    @abstractmethod
    def handle_left_click(self, x: int, y: int) -> None: ...
    @abstractmethod
    def handle_right_click(self, x: int, y: int) -> None: ...

    @abstractmethod
    def draw(self) -> None: ...
