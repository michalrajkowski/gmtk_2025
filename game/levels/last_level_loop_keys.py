# game/levels/level_last_loop_keys.py
from __future__ import annotations
from typing import Dict, List, Optional, Callable, Tuple
import random
import pyxel

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action
from game.objects.door import Door
from game.objects.flag import Flag
from game.objects.locked_wall import LockedWall
from game.objects.toggle_switch import ToggleSwitch
from game.objects.button import Button
from game.objects.pickable import Key
from game.objects.key_gate import KeyGate
from game.objects.ghost_wall import GhostWall

KEY_RED = 2
KEY_GREEN = 3
KEY_BLUE = 4


class LevelLastLoopKeys(LevelBase):
    """
    Rooms:
      A (main):
        - Bottom row: 3 gray covers (closed by default). Behind each: a key (R,G,B) randomized EACH LOOP.
        - Right side: WIN wall (opens when all 3 buttons in F are HELD).
        - Door to F at top-left.

      F (final):
        - A GhostWall that auto-opens on the last loop; behind it a switch.
          The switch OPENS the 3 gray covers in A (so you can pick keys).
        - Three colored KeyGates (R,G,B); behind each a button. Hold ALL THREE to open WIN wall in A.
        - No door back to A (one-way).
    """

    name: str = "Last Loop Keys"
    difficulty: int = 3
    start_room: str = "A"
    max_cursors: int = 6
    loop_seconds: int = 45

    def __init__(self) -> None:
        self._rooms: Dict[str, List[LevelObject]] = {"A": [], "F": []}
        self.completed = False

        # ---------- layout ----------
        W, H = 24, 24

        # MAIN (A)
        self.door_to_F = Door(
            x=24, y=24, w=W, h=H, target_room="F", color=11, label="F"
        )
        self.win_wall = LockedWall(
            x=256, y=56, w=W, h=H, is_open=False, fill=9, border=7
        )
        self.flag = Flag(x=256, y=56, w=W, h=H)
        self.flag.on_finish = self._finish

        # Three gray covers at bottom; keys will sit exactly under these
        y_keys = 140
        xs = [60, 120, 180]  # centered across the bottom
        self._key_slots: List[Tuple[int, int]] = [(x, y_keys) for x in xs]
        self._covers: List[LockedWall] = [
            LockedWall(x=x, y=y_keys, w=W, h=H, is_open=False, fill=5, border=7)
            for x in xs
        ]

        # The 3 key objects (we reposition/randomize each loop)
        self._keys: List[Key] = [
            Key(x=0, y=0, w=0, h=0, room_id="A", color=8, key_id=KEY_RED),
            Key(x=0, y=0, w=0, h=0, room_id="A", color=11, key_id=KEY_GREEN),
            Key(x=0, y=0, w=0, h=0, room_id="A", color=12, key_id=KEY_BLUE),
        ]
        # slot index for each key (filled by _randomize_keys_each_loop/reset_level)
        self._key_slot_idx: Dict[int, int] = {}  # key: id(Key) -> slot index

        self._rooms["A"] = [self.door_to_F, self.win_wall, self.flag] + self._covers

        # FINAL (F)
        # Ghost wall guarding the switch (auto-opens on last loop)
        self.ghost = GhostWall(x=120, y=100, w=W, h=H, open_at_loops_left=1)
        self.switch = ToggleSwitch(x=120, y=100, w=16, h=16, is_on=False)

        # Three colored gates with buttons behind them (same position)
        gx = [60, 140, 220]
        gy = 40
        self.gate_R = KeyGate(x=gx[0], y=gy, w=W, h=H, required_key=KEY_RED, fill=8)
        self.gate_G = KeyGate(x=gx[1], y=gy, w=W, h=H, required_key=KEY_GREEN, fill=11)
        self.gate_B = KeyGate(x=gx[2], y=gy, w=W, h=H, required_key=KEY_BLUE, fill=12)

        # Buttons (centered in each gate cell)
        def btn_pos(wx: int, wy: int, r: int = 10) -> tuple[int, int]:
            return wx + (W - 2 * r) // 2, wy + (H - 2 * r) // 2

        self.btn_R = Button(
            x=btn_pos(self.gate_R.x, self.gate_R.y)[0],
            y=btn_pos(self.gate_R.x, self.gate_R.y)[1],
            w=0,
            h=0,
            radius=10,
        )
        self.btn_G = Button(
            x=btn_pos(self.gate_G.x, self.gate_G.y)[0],
            y=btn_pos(self.gate_G.x, self.gate_G.y)[1],
            w=0,
            h=0,
            radius=10,
        )
        self.btn_B = Button(
            x=btn_pos(self.gate_B.x, self.gate_B.y)[0],
            y=btn_pos(self.gate_B.x, self.gate_B.y)[1],
            w=0,
            h=0,
            radius=10,
        )

        # wire gates to inventory check
        for g in (self.gate_R, self.gate_G, self.gate_B):
            g.can_open = self._actor_has_key

        self._rooms["F"] = [
            self.ghost,
            self.switch,
            self.gate_R,
            self.gate_G,
            self.gate_B,
        ]

        # inventory list (shared)
        self._pickables: List[Key] = list(self._keys)

        # loops-left provider (GameplayScene should set this; default = never open)
        self._get_loops_left: Callable[[], int] = lambda: 999
        self.ghost.set_loops_left_provider(self._get_loops_left)

    # ----- glue for scene -----
    def set_loops_left_provider(self, provider: Callable[[], int]) -> None:
        self._get_loops_left = provider
        self.ghost.set_loops_left_provider(provider)

    # ----- LevelBase -----
    def reset_level(self) -> None:
        """Enter from menu: put keys in a fixed order (no shuffle on level start)."""
        self.completed = False
        self.win_wall.is_open = False
        self.switch.is_on = False
        for c in self._covers:
            c.is_open = False
        self.flag.reset()

        # close colored gates/buttons
        for g in (self.gate_R, self.gate_G, self.gate_B):
            g.reset()
        for b in (self.btn_R, self.btn_G, self.btn_B):
            b.reset()
        self.ghost.reset()

        # Fixed placement on level start (no randomization here)
        for i, key in enumerate(self._keys):
            x, y = self._key_slots[i]
            key.held_by = None
            key.x, key.y = x, y
            key.room_id = "A"
            key.spawn_x, key.spawn_y, key.spawn_room = x, y, "A"
            self._key_slot_idx[id(key)] = i

    def on_loop_start(self) -> None:
        """Each new loop: shuffle RGB key order."""
        self.completed = False
        self.win_wall.is_open = False
        self.switch.is_on = False
        for c in self._covers:
            c.is_open = False

        # reset gates/buttons per loop
        for g in (self.gate_R, self.gate_G, self.gate_B):
            g.reset()
        for b in (self.btn_R, self.btn_G, self.btn_B):
            b.reset()
        self.ghost.reset()

        # Randomize key order each loop (and drop to ground)
        self._randomize_keys_each_loop()

    # ----- helpers -----
    def _finish(self) -> None:
        self.completed = True

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

    def _randomize_keys_each_loop(self) -> None:
        """Place the three keys at the three bottom slots in random order; drop them on the ground."""
        order = list(range(len(self._keys)))  # [0,1,2]
        random.shuffle(order)
        for key, slot_idx in zip(self._keys, order):
            x, y = self._key_slots[slot_idx]
            key.held_by = None
            key.x, key.y = x, y
            key.room_id = "A"
            self._key_slot_idx[id(key)] = slot_idx

    def _slot_cover_open_for_key(self, key: Key) -> bool:
        slot = self._key_slot_idx.get(id(key), -1)
        if 0 <= slot < len(self._covers):
            return self._covers[slot].is_open
        return False

    # ----- per-frame hooks -----
    def on_actor_frame(self, actor_id: int, x: int, y: int, room_id: str) -> None:
        # 1) Ghost wall auto-open on last loop
        self.ghost.update_auto_open()

        # 2) Move any carried keys with their owner
        for k in self._pickables:
            k.on_actor_frame(actor_id, x, y, room_id)

        # 3) While all three buttons are held (in room F), keep the WIN wall open
        all_held = self.btn_R.lit and self.btn_G.lit and self.btn_B.lit
        self.win_wall.is_open = all_held

        # 4) Instantly reflect the switch state in A (even if a ghost pressed it in F)
        for c in self._covers:
            c.is_open = self.switch.is_on

    # ----- input -----
    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        active_id = getattr(self, "_active_actor_id", -999)
        if room_id not in ("A", "F"):
            return None

        if room_id == "A":
            # door to F
            if action == "press":
                _spawned, evt = self.door_to_F.handle_input(which, action, x, y)
                if evt is not None:
                    return evt

            # clicking flag when win wall open
            if self.win_wall.is_open and action == "press":
                self.flag.handle_input(which, action, x, y)

            # grab keys only if their cover is open
            if action == "press":
                for k in self._keys:
                    if k.room_id != "A":
                        continue
                    if not self._slot_cover_open_for_key(k):
                        continue
                    if k.contains(x, y):
                        # drop any currently held item by this actor
                        for other in self._pickables:
                            if other.held_by == active_id:
                                other.held_by = None
                        # take this one
                        k.held_by = active_id
                        break
            return None

        if room_id == "F":
            # Ghost gate blocks the switch visually; only allow switch when open
            if action == "press" and self.ghost._open:
                self.switch.handle_input(which, action, x, y)

            # Gates: open with correct key on press/hold
            if action in ("press", "hold"):
                for g in (self.gate_R, self.gate_G, self.gate_B):
                    _spawned, evt = g.handle_input(which, action, x, y)
                    if evt is not None:
                        return evt

            # Buttons behind the gates are hold-only; only handle when gate is open
            if self.gate_R.is_open:
                self.btn_R.handle_input(which, action, x, y)
            if self.gate_G.is_open:
                self.btn_G.handle_input(which, action, x, y)
            if self.gate_B.is_open:
                self.btn_B.handle_input(which, action, x, y)

            return None

        return None

    # ----- rendering -----
    def draw_room(self, room_id: str) -> None:
        if room_id == "A":
            pyxel.cls(1)
            # top-left: door to F
            self.door_to_F.draw()

            # right: win area
            if self.win_wall.is_open:
                self.flag.draw()
            else:
                self.win_wall.draw()

            # covers (always draw; they absorb clicks when closed)
            for c in self._covers:
                c.draw()
            return

        if room_id == "F":
            pyxel.cls(1)

            # ghost or switch
            if not self.ghost._open:
                self.ghost.draw()
            else:
                self.switch.draw()

            # gates & (behind-open) buttons
            for g in (self.gate_R, self.gate_G, self.gate_B):
                g.draw()
            if self.gate_R.is_open:
                self.btn_R.draw()
            if self.gate_G.is_open:
                self.btn_G.draw()
            if self.gate_B.is_open:
                self.btn_B.draw()
            return

    def draw_room_overlay(self, room_id: str) -> None:
        """
        Draw keys above everything:
        - If a key is HELD, draw it whenever it's in the current room.
        - If a key is on the ground in room A, draw it only if its cover is open.
        - Ground keys in other rooms (not used here) draw unconditionally.
        """
        for k in self._keys:
            if k.room_id != room_id:
                continue
            if k.held_by is None:
                if room_id == "A" and not self._slot_cover_open_for_key(k):
                    continue
            k.draw()
