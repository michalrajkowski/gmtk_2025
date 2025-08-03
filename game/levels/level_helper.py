from __future__ import annotations
from typing import Dict, List, Optional, Callable
import random
import pyxel

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action
from game.objects.pickable import Key
from game.objects.locked_wall import LockedWall
from game.objects.button import Button
from game.objects.flag import Flag
from game.objects.ghost_wall import GhostWall
from game.objects.key_gate import KeyGate

KEY_YELLOW = 1
KEY_RED = 2
KEY_GREEN = 3
KEY_BLUE = 4


class LevelHelper(LevelBase):
    name: str = "Helper"
    difficulty: int = 2
    start_room: str = "A"
    max_cursors: int = 4
    loop_seconds: int = 15

    def __init__(self) -> None:
        self._rooms: Dict[str, List[LevelObject]] = {"A": []}
        self._pickables: List[Key] = []

        # --- Layout constants ---
        W, H = 24, 24
        y_top, y_mid, y_bot = 40, 84, 128

        # Left column: 3 ghost walls that spawn keys EXACTLY where they stood
        x_left = 24
        self.gw_top = GhostWall(x=x_left, y=y_top, w=W, h=H, open_at_loops_left=1)
        self.gw_mid = GhostWall(x=x_left, y=y_mid, w=W, h=H, open_at_loops_left=1)
        self.gw_bot = GhostWall(x=x_left, y=y_bot, w=W, h=H, open_at_loops_left=1)
        for gw in (self.gw_top, self.gw_mid, self.gw_bot):
            gw.spawn_room = "A"
            gw.spawn_pos = (gw.x, gw.y)  # spawn the key at the wall position

        # Center: golden wall + flag behind it
        self.center = LockedWall(
            x=138, y=y_mid, w=W, h=H, is_open=False, fill=9, border=7
        )
        self.flag = Flag(x=138, y=y_mid, w=W, h=H)
        self.flag.on_finish = self._finish

        # Right column: RGB key gates (open → button appears exactly in-place)
        x_right = 260
        self.gate_R = KeyGate(
            x=x_right, y=y_top, w=W, h=H, required_key=KEY_RED, fill=8
        )
        self.gate_G = KeyGate(
            x=x_right, y=y_mid, w=W, h=H, required_key=KEY_GREEN, fill=11
        )
        self.gate_B = KeyGate(
            x=x_right, y=y_bot, w=W, h=H, required_key=KEY_BLUE, fill=12
        )
        for g in (self.gate_R, self.gate_G, self.gate_B):
            g.can_open = self._actor_has_key

        # Buttons that are revealed exactly where the gates were
        # Button.x/y are top-left of its circle’s bounding box; radius 10 fits nicely in 24px cell
        r = 10

        def btn_pos(wx: int, wy: int) -> tuple[int, int]:
            return wx + (W - 2 * r) // 2, wy + (H - 2 * r) // 2

        brx, bry = btn_pos(self.gate_R.x, self.gate_R.y)
        bgx, bgy = btn_pos(self.gate_G.x, self.gate_G.y)
        bbx, bby = btn_pos(self.gate_B.x, self.gate_B.y)

        self.btn_R = Button(x=brx, y=bry, w=0, h=0, radius=r)
        self.btn_G = Button(x=bgx, y=bgy, w=0, h=0, radius=r)
        self.btn_B = Button(x=bbx, y=bby, w=0, h=0, radius=r)

        # Wire room objects (no buttons/keys here; those are conditional)
        self._rooms["A"] = [
            self.gw_top,
            self.gw_mid,
            self.gw_bot,
            self.gate_R,
            self.gate_G,
            self.gate_B,
            self.center,
            self.flag,
        ]

        # Randomize which key spawns behind each ghost wall
        self._randomize_ghost_keys()

        # default provider; GameplayScene will set the real one
        self._get_loops_left: Callable[[], int] = lambda: 999

        self._center_opened: bool = False

    # --- wiring from scene (GameplayScene will call this once) ---
    def set_loops_left_provider(self, provider: Callable[[], int]) -> None:
        self._get_loops_left = provider
        for gw in (self.gw_top, self.gw_mid, self.gw_bot):
            gw.set_loops_left_provider(provider)

    # --- LevelBase ---
    def reset_level(self) -> None:
        self.completed = False
        for obj in self._rooms["A"]:
            obj.reset()
        self._pickables.clear()
        self.btn_R.reset()
        self.btn_G.reset()
        self.btn_B.reset()
        self._randomize_ghost_keys()
        # NEW: ensure wall is closed on full reset
        self._center_opened = False
        self.center.is_open = False

    def on_loop_start(self) -> None:
        # NEW: reset the center latch each loop
        self._center_opened = False
        self.center.is_open = False

    def _finish(self) -> None:
        self.completed = True

    # Inventory helpers
    def _actor_has_key(self, actor_id: int, key_id: int) -> bool:
        for k in self._pickables:
            if k.held_by == actor_id and k.key_id == key_id:
                return True
        return False

    def _set_active_actor_on_gates(self, actor_id: int) -> None:
        for g in (self.gate_R, self.gate_G, self.gate_B):
            g.set_active_actor(actor_id)

    def set_active_actor(self, actor_id: int) -> None:
        super().set_active_actor(actor_id)
        self._set_active_actor_on_gates(actor_id)

    # Auto-open ghost walls even with no input; move any carried keys
    def on_actor_frame(self, actor_id: int, x: int, y: int, room_id: str) -> None:
        # open walls automatically at the last loop and spawn keys at wall positions
        for gw in (self.gw_top, self.gw_mid, self.gw_bot):
            spawned = gw.update_auto_open()
            if isinstance(spawned, Key):
                self._pickables.append(spawned)

        for k in self._pickables:
            k.on_actor_frame(actor_id, x, y, room_id)

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        if room_id != "A":
            return None

        # Grab/steal keys
        if action == "press":
            active_id = getattr(self, "_active_actor_id", -999)
            for k in self._pickables:
                if k.room_id == room_id and k.try_grab_or_steal(active_id, x, y):
                    return None

        # Route to room objects (ghost walls, key gates, center, flag)
        for obj in list(self._rooms.get(room_id, [])):
            # Hide flag interaction until center is latched open
            if obj is self.flag and not self._center_opened:
                continue
            spawned, evt = obj.handle_input(which, action, x, y)
            if spawned is not None:
                self._rooms[room_id].append(spawned)
            if evt is not None:
                return evt

        # Buttons are only interactable when their gate is open
        if self.gate_R.is_open:
            self.btn_R.handle_input(which, action, x, y)
        if self.gate_G.is_open:
            self.btn_G.handle_input(which, action, x, y)
        if self.gate_B.is_open:
            self.btn_B.handle_input(which, action, x, y)

        # Latch the center wall open once all three are held in the same frame
        if not self._center_opened and (
            self.btn_R.lit and self.btn_G.lit and self.btn_B.lit
        ):
            self._center_opened = True

        # Keep the wall visually gone once opened; otherwise closed
        self.center.is_open = self._center_opened

        # Allow clicking the flag when latched open
        if self._center_opened:
            self.flag.handle_input(which, action, x, y)

        return None

    def draw_room(self, room_id: str) -> None:
        pyxel.cls(1)
        for obj in self._rooms.get(room_id, []):
            # Don't draw the flag until the center is latched open
            if obj is self.flag and not self._center_opened:
                continue
            obj.draw()

        # Draw buttons exactly where the gates were, but only when opened
        if self.gate_R.is_open:
            self.btn_R.draw()
        if self.gate_G.is_open:
            self.btn_G.draw()
        if self.gate_B.is_open:
            self.btn_B.draw()

    def draw_room_overlay(self, room_id: str) -> None:
        # Keys draw above everything
        for k in self._pickables:
            if k.room_id == room_id:
                k.draw()

    def _randomize_ghost_keys(self) -> None:
        colors = [KEY_RED, KEY_GREEN, KEY_BLUE]
        random.shuffle(colors)
        mapping = [
            (self.gw_top, colors[0]),
            (self.gw_mid, colors[1]),
            (self.gw_bot, colors[2]),
        ]
        for gw, kid in mapping:
            gw.reset()
            gw.spawn_key_id = kid
            gw.spawn_key_color = (
                8 if kid == KEY_RED else (11 if kid == KEY_GREEN else 12)
            )
            gw.spawn_pos = (gw.x, gw.y)  # ensure exact wall position
