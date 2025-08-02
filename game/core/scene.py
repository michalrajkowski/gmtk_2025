from __future__ import annotations

from abc import ABC, abstractmethod


class Scene(ABC):
    @abstractmethod
    def update(self) -> None: ...
    @abstractmethod
    def draw(self) -> None: ...
    def on_enter(self) -> None:  # optional hooks
        return None

    def on_exit(self) -> None:
        return None
