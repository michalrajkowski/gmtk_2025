from __future__ import annotations
from dataclasses import dataclass
from typing import List

import pyxel
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class LockedWall(LevelObject):
    x: int
    y: int
    w: int
    h: int
    is_open: bool = False
    fill: int = 5  # gray fill
    border: int = 7  # white border
    icon_col: int = 7  # lock icon color

    def reset(self) -> None:
        self.is_open = False

    def set_open(self, open_: bool) -> None:
        self.is_open = open_

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        # Not interactable itself. If closed and clicked, it simply absorbs the click.
        if not self.is_open and self.contains(px, py):
            return None, None
        return None, None

    def draw(self) -> None:
        if self.is_open:
            return  # invisible when open
        pyxel.rect(self.x, self.y, self.w, self.h, self.fill)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
        self._draw_lock_icon()

    def _draw_lock_icon(self) -> None:
        """
        Tiny padlock drawn pixel-by-pixel using pset.
        Designed for ~24x24 wall; icon is ~9x10 pixels centered.
        '#' pixels will be plotted in icon_col.
        """
        pattern: List[str] = [
            "...######...",
            "..#......#..",  # shackle top
            ".#........#.",
            "############",
            "####....####",  # body top
            "####....####",  # keyhole column
            "#####..#####",
            "#####..#####",
            "############",  # body bottom
        ]
        iw, ih = len(pattern[0]), len(pattern)
        cx = self.x + self.w // 2
        cy = self.y + self.h // 2
        ox = cx - iw // 2
        oy = cy - ih // 2
        for j, row in enumerate(pattern):
            for i, ch in enumerate(row):
                if ch == "#":
                    pyxel.pset(ox + i, oy + j, self.icon_col)
