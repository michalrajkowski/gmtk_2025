from __future__ import annotations

from dataclasses import dataclass
from typing import List

import pyxel


@dataclass(slots=True)
class Ripple:
    x: int
    y: int
    age: int = 0
    max_age: int = 8
    max_radius: int = 12
    color: int = 7  # draw as a ring (no alpha in Pyxel)

    def update(self) -> bool:
        self.age += 1
        return self.age < self.max_age

    def draw(self) -> None:
        r = int(self.max_radius * self.age / self.max_age)
        if r > 0:
            pyxel.circb(self.x, self.y, r, self.color)


class Effects:
    """Lightweight VFX manager (background layer)."""

    def __init__(self) -> None:
        self._ripples: List[Ripple] = []

    def add_click(self, x: int, y: int, color: int) -> None:
        self._ripples.append(Ripple(x, y, age=0, max_age=8, max_radius=12, color=color))

    def update(self) -> None:
        self._ripples = [r for r in self._ripples if r.update()]

    def draw(self) -> None:
        for r in self._ripples:
            r.draw()
