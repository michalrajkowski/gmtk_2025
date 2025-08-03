# game/objects/four_color_key_wall.py
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, List
import pyxel
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class FourColorKeyWall(LevelObject):
    x: int
    y: int
    w: int
    h: int
    target_room: str

    # key ids (default to 1..4 = Y,R,G,B)
    key_y: int = 1
    key_r: int = 2
    key_g: int = 3
    key_b: int = 4

    # square fills (pyxel palette indices)
    col_y: int = 9
    col_r: int = 8
    col_g: int = 11
    col_b: int = 12
    border: int = 7
    icon_col: int = 7

    can_open: Optional[Callable[[int, int], bool]] = None
    _active_actor_id: Optional[int] = None

    used_y: bool = False
    used_r: bool = False
    used_g: bool = False
    used_b: bool = False
    _open: bool = False

    def reset(self) -> None:
        self.used_y = self.used_r = self.used_g = self.used_b = False
        self._open = False

    def set_active_actor(self, actor_id: int) -> None:
        self._active_actor_id = actor_id

    def _mark_if_holding(self, key_id: int) -> bool:
        return bool(
            self.can_open
            and self._active_actor_id is not None
            and self.can_open(self._active_actor_id, key_id)
        )

    def _all_used(self) -> bool:
        return self.used_y and self.used_r and self.used_g and self.used_b

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        if action != "press":
            return None, None
        if not (self.x <= px < self.x + self.w and self.y <= py < self.y + self.h):
            return None, None

        if not self._open:
            # Which quadrant?
            half_w, half_h = self.w // 2, self.h // 2
            dx, dy = px - self.x, py - self.y
            _ = (dx >= half_w, dy >= half_h)  # computed but not used

            # Try mark based on held key (only one possible at a time)
            if self._mark_if_holding(self.key_y):
                self.used_y = True
            if self._mark_if_holding(self.key_r):
                self.used_r = True
            if self._mark_if_holding(self.key_g):
                self.used_g = True
            if self._mark_if_holding(self.key_b):
                self.used_b = True

            self._open = self._all_used()
            return None, None

        # Open: acts like a door
        return None, CursorEvent(room=self.target_room, teleport_to=None)

    def _draw_lock_icon(self, rx: int, ry: int, rw: int, rh: int) -> None:
        pattern: List[str] = [
            "...######...",
            "..#......#..",
            ".#........#.",
            "############",
            "####....####",
            "####....####",
            "#####..#####",
            "#####..#####",
            "############",
        ]
        iw, ih = len(pattern[0]), len(pattern)
        ox = rx + (rw - iw) // 2
        oy = ry + (rh - ih) // 2
        for j, row in enumerate(pattern):
            for i, ch in enumerate(row):
                if ch == "#":
                    pyxel.pset(ox + i, oy + j, self.icon_col)

    # game/objects/four_color_key_wall.py  (draw)
    def draw(self) -> None:
        if self._open:
            # big black panel + arrow
            pyxel.rect(self.x, self.y, self.w, self.h, 0)
            pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
            pattern = ("..##..", ".####.", "######", "..##..", "..##..", "..##..")
            ih, iw = len(pattern), len(pattern[0])
            ox = self.x + (self.w - iw) // 2
            oy = self.y + (self.h - ih) // 2
            for j, row in enumerate(pattern):
                for i, ch in enumerate(row):
                    if ch == "#":
                        pyxel.pset(ox + i, oy + j, self.border)
            return

        # (existing locked-state drawing with 4 colored tiles + tiny locks)
        half_w, half_h = self.w // 2, self.h // 2
        quads = [
            (self.x, self.y, half_w, half_h, self.col_y, self.used_y),
            (self.x + half_w, self.y, half_w, half_h, self.col_r, self.used_r),
            (self.x, self.y + half_h, half_w, half_h, self.col_g, self.used_g),
            (self.x + half_w, self.y + half_h, half_w, half_h, self.col_b, self.used_b),
        ]
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)
        for rx, ry, rw, rh, col, used in quads:
            pyxel.rect(rx, ry, rw, rh, col)
            pyxel.rectb(rx, ry, rw, rh, self.border)
            if not used:
                self._draw_lock_icon(rx, ry, rw, rh)
