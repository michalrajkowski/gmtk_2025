from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Tuple


@dataclass(slots=True)
class CursorCtx:
    room: str
    offset_x: int = 0
    offset_y: int = 0


@dataclass(slots=True)
class CursorEvent:
    # If set, the cursor switches to this room
    room: Optional[str] = None
    # If set, the cursor teleports to this absolute position (window coords)
    teleport_to: Optional[Tuple[int, int]] = None


def apply_event(ctx: CursorCtx, event: CursorEvent, raw_x: int, raw_y: int) -> None:
    if event.room is not None:
        ctx.room = event.room
    if event.teleport_to is not None:
        tx, ty = event.teleport_to
        # keep using recorded raw positions, but adjust with an offset so the
        # rendered/interaction position snaps to the teleport target
        ctx.offset_x = tx - raw_x
        ctx.offset_y = ty - raw_y
