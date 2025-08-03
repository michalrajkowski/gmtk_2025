from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Optional, Tuple, List

import pyxel
from game.objects.base import LevelObject, Which, Action
from game.objects.pickable import Key


@dataclass(slots=True)
class GhostWall(LevelObject):
    x: int
    y: int
    w: int
    h: int

    # Opens automatically when (loops_left <= open_at_loops_left)
    open_at_loops_left: int = 1

    # Visuals
    fill: int = 0
    border: int = 2
    text_col: int = 10  # purple text
    icon_col: int = 10  # purple hourglass

    # Injected by scene/level (returns an integer like: current_loop_including_this_one)
    _get_loops_left: Optional[Callable[[], int]] = None

    # State
    _open: bool = False
    _has_spawned: bool = False

    # Optional auto-spawned key when opening
    spawn_room: str = "A"
    # NOTE: by default we spawn exactly at (x, y) — i.e., where the wall is.
    spawn_pos: Tuple[int, int] = None  # type: ignore[assignment]
    spawn_key_id: Optional[int] = None
    spawn_key_color: int = 9

    def __post_init__(self) -> None:
        if self.spawn_pos is None:
            self.spawn_pos = (self.x, self.y)

    def set_loops_left_provider(self, fn: Callable[[], int]) -> None:
        self._get_loops_left = fn

    def reset(self) -> None:
        self._open = False
        self._has_spawned = False

    # Call this every frame (from the level) to auto-open
    def update_auto_open(self) -> Optional[Key]:
        if self._open:
            return None
        loops_left = self._get_loops_left() if self._get_loops_left else 999
        if loops_left <= self.open_at_loops_left:
            self._open = True
            if (not self._has_spawned) and (self.spawn_key_id is not None):
                self._has_spawned = True
                kx, ky = self.spawn_pos
                return Key(
                    x=kx,
                    y=ky,
                    w=0,
                    h=0,
                    room_id=self.spawn_room,
                    color=self.spawn_key_color,
                    key_id=int(self.spawn_key_id),
                )
        return None

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        # No interaction required; opens via update_auto_open()
        return None, None

    def draw(self) -> None:
        if self._open:
            return  # invisible when opened

        # Wall body
        pyxel.rect(self.x, self.y, self.w, self.h, self.fill)
        pyxel.rectb(self.x, self.y, self.w, self.h, self.border)

        # Hourglass pixel pattern (12x9)
        pattern: List[str] = [
            ".##########.",
            ".#........#.",
            "..#......#..",
            "...##..##...",
            ".....##.....",
            "...##..##...",
            "..#......#..",
            ".#........#.",
            ".##########.",
        ]
        ih = len(pattern)
        iw = len(pattern[0]) if ih > 0 else 0
        scale = 1  # fits nicely inside a 24x24 cell

        # Center the icon within the wall
        ox = self.x + (self.w - iw * scale) // 2
        oy = self.y + (self.h - ih * scale) // 2 - 3  # nudge up to leave room for text

        for j, row in enumerate(pattern):
            for i, ch in enumerate(row):
                if ch == "#":
                    px = ox + i * scale
                    py = oy + j * scale
                    pyxel.rect(px, py, scale, scale, self.icon_col)

        # Label: "on last loop" (purple) near the bottom of the tile
        label = "on last loop"
        tw = len(label) * 4
        tx = self.x + (self.w - tw) // 2
        ty = self.y + self.h - 8
        pyxel.text(tx, ty, label, self.text_col)
