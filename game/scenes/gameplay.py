from __future__ import annotations
from typing import Callable, Final, List, Tuple, Dict

import pyxel

from game.core.effects import Effects
from game.core.timeline import GhostSample, TimelineManager
from game.core.cursor import CursorCtx, apply_event
from game.levels.level_base import LevelBase


class GameplayScene:
    # Key mappings
    KEY_QUIT: Final[int] = pyxel.KEY_Q
    KEY_MENU: Final[int] = pyxel.KEY_L
    KEY_RESTART: Final[int] = pyxel.KEY_R
    KEY_PASS: Final[int] = pyxel.KEY_P
    KEY_COMMIT_ALT: Final[int] = pyxel.KEY_RETURN
    KEY_BACK_ALT: Final[int] = pyxel.KEY_ESCAPE

    NAV_H: Final[int] = 16
    NAV_GAP: Final[int] = 4
    NAV_PAD_X: Final[int] = 4
    NAV_PAD_Y: Final[int] = 3

    def __init__(
        self,
        level: LevelBase,
        draw_pointer: Callable[[int, int, int, int], None],
        width: int,
        height: int,
        fps: int,
        loop_seconds: int,
        exit_to_menu: Callable[[], None] | None = None,
        on_level_completed: Callable[[str], None] | None = None,
    ) -> None:
        self._level = level
        self._draw_pointer = draw_pointer
        self._w: Final[int] = width
        self._h: Final[int] = height

        self._fps: Final[int] = fps
        self._loop_frames: Final[int] = loop_seconds * fps

        self._timelines = TimelineManager(max_frames=self._loop_frames)
        self._fx_ghost, self._fx_player = Effects(), Effects()
        self._tick = 0
        self._render_tick = 0

        # Snapshots
        self._mouse_raw_x = 0
        self._mouse_raw_y = 0
        self._mouse_eff_x = 0
        self._mouse_eff_y = 0

        # Per-cursor contexts
        self._player_ctx: CursorCtx = CursorCtx(room=getattr(level, "start_room", "A"))
        self._ghost_ctxs: List[CursorCtx] = []

        # Cursors (lives)
        self._max_cursors: int = getattr(level, "max_cursors", 10)
        self._cursors_left: int = self._max_cursors

        self._exit_to_menu = exit_to_menu
        self._on_level_completed = on_level_completed

        self._nav_rects: Dict[str, Tuple[int, int, int, int]] = {}

        # Start first loop (consumes a cursor)
        self._consume_and_start_new_loop()

    # ----- lifecycle -----
    def _start_new_loop_core(self) -> None:
        self._level.on_loop_start()
        self._timelines.start_run()
        self._fx_ghost = Effects()
        self._fx_player = Effects()
        self._tick = 0
        self._render_tick = 0
        self._player_ctx = CursorCtx(room=getattr(self._level, "start_room", "A"))
        self._ghost_ctxs = [
            CursorCtx(room=self._player_ctx.room) for _ in self._timelines.past_runs
        ]

    def _consume_and_start_new_loop(self) -> None:
        # If out of cursors, reset level & timelines and refill
        if self._cursors_left <= 0:
            self._timelines.reset_all()
            self._level.reset_level()
            self._cursors_left = self._max_cursors
        # Consume a cursor and begin loop
        self._cursors_left -= 1
        self._start_new_loop_core()

    def _commit_and_start_next(self) -> None:
        self._timelines.end_run()
        self._consume_and_start_new_loop()

    def _restart_discard_current(self) -> None:
        self._timelines.discard_run()
        self._consume_and_start_new_loop()

    # ----- nav -----
    def _measure_btn(self, label: str) -> int:
        return len(label) * 4 + self.NAV_PAD_X * 2 + 2

    def _layout_nav(self) -> None:
        x = self.NAV_GAP
        y = 0
        h = self.NAV_H
        self._nav_rects.clear()

        labels = {
            "levels": "[L]evels",
            "name": f"{getattr(self._level, 'name', 'Level')}",
            "restart": "[R]estart",
            "pass": "[P]ass",
        }
        for key in ["levels", "name", "restart", "pass"]:
            w = self._measure_btn(labels[key])
            self._nav_rects[key] = (x, y, w, h)
            x += w + self.NAV_GAP

        # Right-aligned labels: time + cursors
        # (store as rects for consistent look; not clickable)
        time_txt = self._format_time_label()
        cur_txt = self._format_cursors_label()
        cur_w = self._measure_btn(cur_txt)
        time_w = self._measure_btn(time_txt)

        cur_x = self._w - self.NAV_GAP - cur_w
        time_x = cur_x - self.NAV_GAP - time_w

        self._nav_rects["time"] = (time_x, y, time_w, h)
        self._nav_rects["cursors"] = (cur_x, y, cur_w, h)

    def _time_color(self) -> int:
        secs_left = max(0.0, (self._loop_frames - self._render_tick) / self._fps)
        if secs_left <= 3.0:
            return 8  # red
        if secs_left <= 5.0:
            return 10  # yellow
        return 7  # white

    def _format_time_label(self) -> str:
        secs_left = max(0.0, (self._loop_frames - self._render_tick) / self._fps)
        return f"Time: {secs_left:0.1f}s"

    def _cursors_color(self) -> int:
        return 8 if self._cursors_left == 0 else 7

    def _format_cursors_label(self) -> str:
        return f"{self._cursors_left + 1}/{self._max_cursors}"

    def _draw_nav(self) -> None:
        pyxel.rect(0, 0, self._w, self.NAV_H, 0)

        def center_text(x: int, w: int, y: int, txt: str, col: int) -> None:
            tw = len(txt) * 4
            tx = x + (w - tw) // 2
            ty = y + (self.NAV_H - 6) // 2
            pyxel.text(tx, ty, txt, col)

        labels = {
            "levels": "[L]evels",
            "name": f"{getattr(self._level, 'name', 'Level')}",
            "restart": "[R]estart",
            "pass": "[P]ass",
            "time": self._format_time_label(),
            "cursors": self._format_cursors_label(),
        }
        colors = {
            "levels": 7,
            "name": 7,
            "restart": 7,
            "pass": 7,
            "time": self._time_color(),
            "cursors": self._cursors_color(),
        }

        for key, (x, y, w, h) in self._nav_rects.items():
            pyxel.rectb(x, y, w, h, 7)
            center_text(x, w, y, labels[key], colors[key])

    def _handle_nav_click(self, mx: int, my: int) -> bool:
        if my >= self.NAV_H:
            return False
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for key, (x, y, w, h) in self._nav_rects.items():
                if key in ("time", "cursors"):
                    continue  # not clickable
                if x <= mx < x + w and y <= my < y + h:
                    if key == "levels" and self._exit_to_menu:
                        self._exit_to_menu()
                        return True
                    if key == "restart":
                        self._restart_discard_current()
                        return True
                    if key == "pass":
                        self._commit_and_start_next()
                        return True
        return False

    # ----- update/draw -----
    def update(self) -> None:
        self._layout_nav()

        # Global keys
        if pyxel.btnp(self.KEY_QUIT):
            pyxel.quit()
            return
        if self._exit_to_menu and pyxel.btnp(self.KEY_MENU):
            self._exit_to_menu()
            return
        if pyxel.btnp(self.KEY_RESTART):
            self._restart_discard_current()
            return
        if pyxel.btnp(self.KEY_PASS) or pyxel.btnp(self.KEY_COMMIT_ALT):
            self._commit_and_start_next()
            return
        if self._exit_to_menu and pyxel.btnp(self.KEY_BACK_ALT):
            self._exit_to_menu()
            return
        if pyxel.btnp(pyxel.KEY_N):
            # Hard reset: refill cursors and reset timelines/level
            self._timelines.reset_all()
            self._level.reset_level()
            self._cursors_left = self._max_cursors
            self._consume_and_start_new_loop()
            return

        # Clamp + snapshot raw
        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))
        self._mouse_raw_x, self._mouse_raw_y = mx, my

        # Nav click (consume)
        if self._handle_nav_click(mx, my):
            self._timelines.record_frame(mx, my, False, False, False, False)
            self._fx_ghost.update()
            self._fx_player.update()
            self._render_tick = self._tick
            self._tick += 1
            if self._tick >= self._loop_frames:
                self._commit_and_start_next()
            return

        # Buttons: press + hold
        left_p = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT))
        right_p = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT))
        left_h = bool(pyxel.btn(pyxel.MOUSE_BUTTON_LEFT))
        right_h = bool(pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT))

        # Record frame (raw)
        self._timelines.record_frame(mx, my, left_p, right_p, left_h, right_h)

        # --- GHOSTS ---
        ghosts: List[GhostSample] = self._timelines.ghosts_for_frame(self._tick)
        while len(self._ghost_ctxs) < len(ghosts):
            self._ghost_ctxs.append(CursorCtx(room=self._player_ctx.room))

        for idx, g in enumerate(ghosts):
            ctx = self._ghost_ctxs[idx]
            gx = max(0, min(self._w - 1, int(g.x) + ctx.offset_x))
            gy = max(0, min(self._h - 1, int(g.y) + ctx.offset_y))

            if (g.left_p or g.right_p) and ctx.room == self._player_ctx.room:
                self._fx_ghost.add_click(gx, gy, int(g.color))

            if g.left_p:
                evt = self._level.interact("L", "press", gx, gy, ctx.room)
                if evt is not None:
                    apply_event(ctx, evt, int(g.x), int(g.y))
            if g.right_p:
                evt = self._level.interact("R", "press", gx, gy, ctx.room)
                if evt is not None:
                    apply_event(ctx, evt, int(g.x), int(g.y))

            if g.left_h:
                evt = self._level.interact("L", "hold", gx, gy, ctx.room)
                if evt is not None:
                    apply_event(ctx, evt, int(g.x), int(g.y))
            if g.right_h:
                evt = self._level.interact("R", "hold", gx, gy, ctx.room)
                if evt is not None:
                    apply_event(ctx, evt, int(g.x), int(g.y))

        # --- PLAYER ---
        px_eff = max(0, min(self._w - 1, mx + self._player_ctx.offset_x))
        py_eff = max(0, min(self._h - 1, my + self._player_ctx.offset_y))
        self._mouse_eff_x, self._mouse_eff_y = px_eff, py_eff

        if left_p or right_p:
            self._fx_player.add_click(px_eff, py_eff, 7)
            if left_p:
                evt = self._level.interact(
                    "L", "press", px_eff, py_eff, self._player_ctx.room
                )
                if evt is not None:
                    apply_event(self._player_ctx, evt, mx, my)
            if right_p:
                evt = self._level.interact(
                    "R", "press", px_eff, py_eff, self._player_ctx.room
                )
                if evt is not None:
                    apply_event(self._player_ctx, evt, mx, my)

        if left_h:
            evt = self._level.interact(
                "L", "hold", px_eff, py_eff, self._player_ctx.room
            )
            if evt is not None:
                apply_event(self._player_ctx, evt, mx, my)
        if right_h:
            evt = self._level.interact(
                "R", "hold", px_eff, py_eff, self._player_ctx.room
            )
            if evt is not None:
                apply_event(self._player_ctx, evt, mx, my)

        # Update effects
        self._fx_ghost.update()
        self._fx_player.update()

        # Completion?
        if getattr(self._level, "completed", False) and self._on_level_completed:
            self._on_level_completed(getattr(self._level, "name", "Level"))
            return

        # Advance
        self._render_tick = self._tick
        self._tick += 1
        if self._tick >= self._loop_frames:
            self._commit_and_start_next()

    def draw(self) -> None:
        pyxel.cls(1)
        self._level.draw_room(self._player_ctx.room)
        self._fx_ghost.draw()

        ghosts = self._timelines.ghosts_for_frame(self._render_tick)
        for idx, g in enumerate(ghosts):
            if idx >= len(self._ghost_ctxs):
                continue
            ctx = self._ghost_ctxs[idx]
            if ctx.room != self._player_ctx.room:
                continue
            gx = int(g.x) + ctx.offset_x
            gy = int(g.y) + ctx.offset_y
            if 0 <= gx < self._w and 0 <= gy < self._h:
                self._draw_pointer(int(gx), int(gy), int(g.color), int(0))

        self._fx_player.draw()
        self._draw_pointer(
            int(self._mouse_eff_x), int(self._mouse_eff_y), int(7), int(0)
        )
        self._draw_nav()
