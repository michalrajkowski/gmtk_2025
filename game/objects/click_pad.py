from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Literal, Optional

import pyxel

Which = Literal["L", "R"]


@dataclass(slots=True)
class ClickPad:
    x: int
    y: int
    w: int
    h: int
    threshold: int  # total clicks needed
    color: int = 3  # base fill color
    border: int = 7  # border color
    on_click: Optional[Callable[["ClickPad", Which, int, int], None]] = None

    # runtime state
    count: int = 0  # clicks received this loop

    def reset(self) -> None:
        """Reset per-loop state (called every new timeline)."""
        self.count = 0

    @property
    def remaining(self) -> int:
        return max(0, self.threshold - self.count)

    @property
    def is_complete(self) -> bool:
        return self.count >= self.threshold

    def contains(self, px: int, py: int) -> bool:
        return self.x <= px < self.x + self.w and self.y <= py < self.y + self.h

    def handle_click(self, which: Which, px: int, py: int) -> None:
        """Respond to a single-frame L/R click. Both decrement progress."""
        if self.is_complete:
            return
        if not self.contains(px, py):
            return
        self.count += 1
        if self.on_click is not None:
            self.on_click(self, which, px, py)

    def draw(self) -> None:
        # Completed pads get a brighter fill
        fill = 11 if self.is_complete else self.color
        pyxel.rect(self.x, self.y, self.w, self.h, fill)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)

        # Minimal, object-local display: remaining countdown centered above
        text = str(self.remaining)
        tw = len(text) * 4  # pyxel.text is 4px per char width
        tx = self.x + (self.w - tw) // 2
        ty = self.y - 8
        pyxel.text(tx, ty, text, 7)
