# game/levels/level_secret_code.py
from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import random
import pyxel

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action
from game.objects.toggle_switch import ToggleSwitch
from game.objects.locked_wall import LockedWall
from game.objects.door import Door
from game.objects.flag import Flag


class LevelSecretCode(LevelBase):
    name: str = "Secret Code"
    difficulty: int = 2
    start_room: str = "A"
    max_cursors: int = 2
    loop_seconds: int = 20

    def __init__(self) -> None:
        self._rooms: Dict[str, List[LevelObject]] = {"A": [], "CODE": []}

        # --- Layout constants ---
        W, H = 24, 24
        # Top row positions
        self._door_x, self._door_y = 24, 24  # top-left: to CODE room
        self._final_x, self._final_y = 252, 24  # top-right: final wall/flag

        # Bottom row positions
        self._switch_x, self._switch_y = 24, 160  # bottom-left: main switch
        r = 10
        bx0 = 120  # first code button x
        bdx = 36  # spacing between buttons
        by = 154  # top-left of circle bbox (center is +r,+r)

        # Main room: door to CODE is hidden by a wall toggled by the bottom switch
        self.sw_main = ToggleSwitch(
            x=self._switch_x, y=self._switch_y, w=16, h=16, is_on=False
        )
        self.wall_to_code = LockedWall(
            x=self._door_x, y=self._door_y, w=W, h=H, is_open=False
        )
        self.door_to_code = Door(
            x=self._door_x,
            y=self._door_y,
            w=W,
            h=H,
            target_room="CODE",
            color=11,
            label="CODE",
        )

        # Final area: wall hides flag until solved
        self.final_wall = LockedWall(
            x=self._final_x, y=self._final_y, w=W, h=H, is_open=False
        )
        self.flag = Flag(x=self._final_x, y=self._final_y, w=W, h=H)
        self.flag.on_finish = self._finish  # make flag end the level

        # Four code buttons (drawn as circles). Store as (id, x, y, r, pressed?)
        self._buttons: List[Tuple[int, int, int, int, bool]] = [
            (1, bx0 + 0 * bdx, by, r, False),
            (2, bx0 + 1 * bdx, by, r, False),
            (3, bx0 + 2 * bdx, by, r, False),
            (4, bx0 + 3 * bdx, by, r, False),
        ]

        # Grey covers that can drop over the buttons after code reveal
        # Sized slightly larger than the circle (2r+4) and centered on button bbox.
        self._btn_covers: List[LockedWall] = []
        for _idx, bx, by, br, _p in self._buttons:
            cover = LockedWall(
                x=bx - 2,
                y=by - 2,
                w=(2 * br) + 4,
                h=(2 * br) + 4,
                is_open=True,
                fill=5,
                border=7,
            )
            self._btn_covers.append(cover)

        # CODE room: a one-shot reveal switch per loop
        self.sw_reveal = ToggleSwitch(x=120, y=80, w=16, h=16, is_on=False)
        self._code_revealed: bool = False

        # Secret code state
        self._secret_code: List[int] = [1, 3, 2, 4]  # overwritten on reset()
        self._input_order: List[int] = []
        self._final_open: bool = False

        # Rooms
        self._rooms["A"] = [
            self.sw_main,
            self.wall_to_code,
            self.door_to_code,
            self.final_wall,
            self.flag,
            # covers are drawn/handled manually to control z-order; not added here
        ]
        self._rooms["CODE"] = [self.sw_reveal]

    # ----- helpers -----
    def _finish(self) -> None:
        self.completed = True

    @staticmethod
    def _circle_contains(px: int, py: int, bx: int, by: int, r: int) -> bool:
        cx, cy = bx + r, by + r
        dx, dy = px - cx, py - cy
        return dx * dx + dy * dy <= r * r

    def _reset_buttons(self) -> None:
        self._input_order.clear()
        self._buttons = [
            (idx, bx, by, br, False) for (idx, bx, by, br, _p) in self._buttons
        ]

    def _all_buttons_pressed(self) -> bool:
        return all(p for (_idx, _bx, _by, _br, p) in self._buttons)

    def _try_press_button(self, idx_to_press: int) -> None:
        if self._final_open:
            return
        # Only press if that button is currently red (not pressed)
        new_buttons: List[Tuple[int, int, int, int, bool]] = []
        pressed_now = False
        for idx, bx, by, br, pressed in self._buttons:
            if idx == idx_to_press and not pressed:
                pressed = True
                pressed_now = True
            new_buttons.append((idx, bx, by, br, pressed))
        self._buttons = new_buttons

        if not pressed_now:
            return

        self._input_order.append(idx_to_press)

        if self._all_buttons_pressed():
            if self._input_order == self._secret_code:
                self._final_open = True
                self.final_wall.is_open = True
            else:
                self._final_open = False
                self.final_wall.is_open = False
                self._reset_buttons()

    # ----- LevelBase -----
    def reset_level(self) -> None:
        # New random permutation each time you enter from the menu
        self._secret_code = random.sample([1, 2, 3, 4], 4)
        self._final_open = False
        self.final_wall.is_open = False

        # Switches OFF on level load
        self.sw_main.is_on = False
        self.wall_to_code.is_open = False
        self.sw_reveal.is_on = False
        self._code_revealed = False

        # Unlock button covers on reset
        for c in self._btn_covers:
            c.is_open = True

        # Flag fresh
        self.flag.reset()

        # Buttons reset
        self._reset_buttons()

    def on_loop_start(self) -> None:
        # Reset every loop
        self._final_open = False
        self.final_wall.is_open = False

        self.sw_main.is_on = False
        self.wall_to_code.is_open = False

        self.sw_reveal.is_on = False
        self._code_revealed = False

        # Unlock covers each loop start
        for c in self._btn_covers:
            c.is_open = True

        self._reset_buttons()

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        if room_id == "A":
            if action == "press":
                # Main switch toggles the top-left wall
                self.sw_main.handle_input(which, action, x, y)
                self.wall_to_code.is_open = self.sw_main.is_on

                # Door to CODE is clickable only when the wall is open
                if self.wall_to_code.is_open:
                    _spawned, evt = self.door_to_code.handle_input(which, action, x, y)
                    if evt is not None:
                        return evt

                # If final wall is open, clicking the flag should finish the level
                if self._final_open:
                    self.flag.handle_input(which, action, x, y)

                # If any cover is closed and the click is on it, absorb and stop
                for cover in self._btn_covers:
                    if not cover.is_open and cover.contains(x, y):
                        cover.handle_input(which, action, x, y)  # absorbs
                        return None

                # Buttons (bottom row): press only if currently red
                for idx, bx, by, br, pressed in self._buttons:
                    if not pressed and self._circle_contains(x, y, bx, by, br):
                        self._try_press_button(idx)
                        break

            return None

        if room_id == "CODE":
            if action == "press":
                # One-shot reveal per loop: set ON; don't allow un-toggle
                if (
                    self.sw_reveal.x <= x < self.sw_reveal.x + self.sw_reveal.w
                    and self.sw_reveal.y <= y < self.sw_reveal.y + self.sw_reveal.h
                ):
                    self.sw_reveal.is_on = True
                    self._code_revealed = True
                    # Lock the main-room buttons behind grey walls until next reset/loop
                    for c in self._btn_covers:
                        c.is_open = False
            return None

        return None

    def draw_room(self, room_id: str) -> None:
        pyxel.cls(1)

        if room_id == "A":
            # Top-left: either wall or (when open) the door
            if self.wall_to_code.is_open:
                self.door_to_code.draw()
            else:
                self.wall_to_code.draw()

            # Top-right: final area
            if not self._final_open:
                self.final_wall.draw()
            else:
                self.flag.draw()

            # Bottom-left switch
            self.sw_main.draw()

            # Buttons: red (off) / green (on)
            for idx, bx, by, br, pressed in self._buttons:
                cx, cy = bx + br, by + br
                fill_col = 11 if pressed else 8  # green if on; red if off
                pyxel.circ(cx, cy, br, fill_col)
                pyxel.circb(cx, cy, br, 7)
                pyxel.text(cx - 2, cy - 2, str(idx), 0)

            # Draw covers last so they visually block buttons
            for cover in self._btn_covers:
                cover.draw()

            # UI hints
            pyxel.text(self._switch_x, self._switch_y - 10, "", 7)
            pyxel.text(self._door_x, self._door_y - 10, "", 7)
            pyxel.text(self._final_x - 8, self._final_y - 10, "", 7)

        elif room_id == "CODE":
            self.sw_reveal.draw()
            pyxel.text(16, 24, "", 7)
            if self._code_revealed:
                code_str = "".join(str(d) for d in self._secret_code)
                pyxel.text(16, 40, f"Secret code is: {code_str}", 12)

    def draw_room_overlay(self, room_id: str) -> None:
        return None
