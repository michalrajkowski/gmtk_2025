# game/objects/pickable.py
from dataclasses import dataclass
from typing import Optional, Tuple, ClassVar
import pyxel
from game.objects.base import LevelObject, Which, Action


@dataclass(slots=True)
class Pickable(LevelObject):
    x: int
    y: int
    w: int
    h: int
    room_id: str
    color: int = 9
    border: int = 7
    held_by: Optional[int] = None
    follow_offset: Tuple[int, int] = (0, -10)

    # NEW: spawn snapshot
    spawn_x: int = 0
    spawn_y: int = 0
    spawn_room: str = ""

    def __post_init__(self) -> None:
        if not self.spawn_room:
            self.spawn_x = self.x
            self.spawn_y = self.y
            self.spawn_room = self.room_id

    def reset(self) -> None:
        # Drop item back to its spawn point
        self.held_by = None
        self.x = self.spawn_x
        self.y = self.spawn_y
        self.room_id = self.spawn_room

    def on_actor_frame(self, actor_id: int, ax: int, ay: int, room_id: str) -> None:
        if self.held_by == actor_id:
            dx, dy = self.follow_offset
            self.x, self.y = ax + dx, ay + dy
            self.room_id = room_id

    def try_grab_or_steal(self, actor_id: int, px: int, py: int) -> bool:
        if self.contains(px, py):
            self.held_by = actor_id
            return True
        return False

    def handle_input(self, which: Which, action: Action, px: int, py: int):
        return None, None

    def draw(self) -> None:
        pass


@dataclass(slots=True)
class Key(Pickable):
    key_id: int = 1  # e.g., 1=yellow, 2=red, 3=green, 4=blue
    tooth_col: int = 7

    PATTERN: ClassVar[Tuple[str, str, str]] = (
        ".#####........",
        ".#...########.",
        ".#####...#..#.",
    )
    SCALE: ClassVar[int] = 2

    def __post_init__(self) -> None:
        # derive size if missing so hit-test works
        if self.w <= 0 or self.h <= 0:
            self.w = len(self.PATTERN[0]) * self.SCALE
            self.h = len(self.PATTERN) * self.SCALE
        Pickable.__post_init__(self)

    def contains(self, px: int, py: int) -> bool:
        lx, ly = px - self.x, py - self.y
        if lx < 0 or ly < 0:
            return False
        i = lx // self.SCALE
        j = ly // self.SCALE
        if 0 <= j < len(self.PATTERN) and 0 <= i < len(self.PATTERN[0]):
            return True
        return False

    # game/objects/pickable.py  (Key.draw)
    def draw(self) -> None:
        S = self.SCALE
        pat = self.PATTERN

        # pass 1: white edge on '.' that touches a '#'
        for j, row in enumerate(pat):
            for i, ch in enumerate(row):
                if ch != ".":
                    continue
                neigh = (
                    (j > 0 and pat[j - 1][i] == "#")
                    or (j + 1 < len(pat) and pat[j + 1][i] == "#")
                    or (i > 0 and pat[j][i - 1] == "#")
                    or (i + 1 < len(row) and pat[j][i + 1] == "#")
                )
                if neigh:
                    px, py = self.x + i * S, self.y + j * S
                    pyxel.rect(px, py, S, S, 7)  # white

        # pass 2: colored body
        for j, row in enumerate(pat):
            for i, ch in enumerate(row):
                if ch == "#":
                    px, py = self.x + i * S, self.y + j * S
                    pyxel.rect(px, py, S, S, self.color)
