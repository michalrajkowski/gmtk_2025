from __future__ import annotations
from typing import Final, List, Optional

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import Which
from game.objects.click_pad import ClickPad


class LevelPads(LevelBase):
    name: str = "Pads"
    difficulty: int = 1
    start_room: str = "A"  # required by the new flow, though unused here

    PAD_W: Final[int] = 36
    PAD_H: Final[int] = 24
    GAP_X: Final[int] = 12
    GAP_Y: Final[int] = 12

    def __init__(self) -> None:
        left = 8
        top = 20
        w = self.PAD_W
        h = self.PAD_H
        gx = self.GAP_X
        gy = self.GAP_Y

        self.pads: List[ClickPad] = [
            ClickPad(left, top, w, h, threshold=10, color=3),
            ClickPad(left + w + gx, top, w, h, threshold=20, color=4),
            ClickPad(left, top + h + gy, w, h, threshold=30, color=5),
            ClickPad(left + w + gx, top + h + gy, w, h, threshold=100, color=6),
        ]

    # --- New LevelBase API ---
    def interact(
        self, which: Which, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # Pads has no rooms: ignore room_id, just apply the click.
        for p in self.pads:
            p.handle_click(which, x, y)
        return None

    def draw_room(self, room_id: str) -> None:
        # Pads has no rooms: draw all pads.
        for p in self.pads:
            p.draw()

    # --- Lifecycle ---
    def reset_level(self) -> None:
        for p in self.pads:
            p.reset()

    def on_loop_start(self) -> None:
        for p in self.pads:
            p.reset()
