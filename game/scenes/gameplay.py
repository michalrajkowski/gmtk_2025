from __future__ import annotations
from typing import Callable, Final, List, Tuple, Dict

import pyxel

from game.core.effects import Effects
from game.core.timeline import GhostSample, TimelineManager
from game.core.cursor import CursorCtx, apply_event
from game.levels.level_base import LevelBase


class GameplayScene:
    # --- Key mappings (change these to remap controls) ---
    KEY_QUIT: Final[int] = pyxel.KEY_Q
    KEY_MENU: Final[int] = pyxel.KEY_L  # [L]evels
    KEY_RESTART: Final[int] = pyxel.KEY_R  # [R]estart
    KEY_PASS: Final[int] = pyxel.KEY_P  # [P]ass (commit)
    KEY_COMMIT_ALT: Final[int] = pyxel.KEY_RETURN  # Enter still commits
    KEY_BACK_ALT: Final[int] = pyxel.KEY_ESCAPE  # Esc also goes to menu

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
        exit_to_menu: Callable[[], None] | None = None,  # optional
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

        # Snapshots for this frame
        self._mouse_raw_x = 0
        self._mouse_raw_y = 0
        self._mouse_eff_x = 0
        self._mouse_eff_y = 0

        # Per-cursor contexts
        self._player_ctx: CursorCtx = CursorCtx(room=getattr(level, "start_room", "A"))
        self._ghost_ctxs: List[CursorCtx] = []

        self._exit_to_menu = exit_to_menu
        self._start_new_loop()

        # Precomputed nav button rects (id -> rect)
        self._nav_rects: Dict[str, Tuple[int, int, int, int]] = {}

    # ----- lifecycle -----
    def _start_new_loop(self) -> None:
        self._level.on_loop_start()
        self._timelines.start_run()
        self._fx_ghost = Effects()
        self._fx_player = Effects()
        self._tick = 0
        self._render_tick = 0

        # reset contexts each loop
        self._player_ctx = CursorCtx(room=getattr(self._level, "start_room", "A"))
        self._ghost_ctxs = [
            CursorCtx(room=self._player_ctx.room) for _ in self._timelines.past_runs
        ]

    def _commit_and_start_next(self) -> None:
        self._timelines.end_run()
        self._start_new_loop()

    def _restart_discard_current(self) -> None:
        self._timelines.discard_run()
        self._start_new_loop()

    # ----- nav layout & drawing -----
    def _measure_btn(self, label: str) -> int:
        # width = text + padding * 2 + 2 for the border pixels
        return len(label) * 4 + self.NAV_PAD_X * 2 + 2

    def _layout_nav(self) -> None:
        """Compute nav button rectangles left-to-right and store in self._nav_rects."""
        x = self.NAV_GAP
        y = 0
        h = self.NAV_H

        self._nav_rects.clear()

        labels = {
            "levels": "[L]evels",
            "name": f"{getattr(self._level, 'name', 'Level')}",
            "restart": "[R]estart",
            "pass": "[P]ass",
            "time": f"Time left: {max(0.0, (self._loop_frames - self._render_tick) / self._fps):0.1f}s",
        }

        for key in ["levels", "name", "restart", "pass", "time"]:
            w = self._measure_btn(labels[key])
            self._nav_rects[key] = (x, y, w, h)
            x += w + self.NAV_GAP

    def _draw_nav(self) -> None:
        # background bar
        pyxel.rect(0, 0, self._w, self.NAV_H, 0)

        # buttons/labels
        def center_text(x: int, w: int, y: int, txt: str) -> None:
            tw = len(txt) * 4
            tx = x + (w - tw) // 2
            ty = y + (self.NAV_H - 6) // 2  # 6px-ish text height centering
            pyxel.text(tx, ty, txt, 7)

        labels = {
            "levels": "[L]evels",
            "name": f"{getattr(self._level, 'name', 'Level')}",
            "restart": "[R]estart",
            "pass": "[P]ass",
            "time": f"Time left: {max(0.0, (self._loop_frames - self._render_tick) / self._fps):0.1f}s",
        }

        # draw rect borders and text
        for key, (x, y, w, h) in self._nav_rects.items():
            pyxel.rectb(x, y, w, h, 7)
            center_text(x, w, y, labels[key])

    def _handle_nav_click(self, mx: int, my: int) -> bool:
        """Returns True if a nav click was handled (consume the click)."""
        if my >= self.NAV_H:
            return False
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            for key, (x, y, w, h) in self._nav_rects.items():
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
        # Compute nav layout first (used in click handling and draw)
        self._layout_nav()

        # Global controls (keys)
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
            self._timelines.reset_all()
            self._level.reset_level()
            self._start_new_loop()
            return

        # Clamp input to window and snapshot raw coords
        mx = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        my = max(0, min(self._h - 1, int(pyxel.mouse_y)))
        self._mouse_raw_x, self._mouse_raw_y = mx, my

        # Handle nav mouse click for the live player only
        if self._handle_nav_click(mx, my):
            # consume the click (don't spawn effects or interact with level)
            # still record a "no-action" frame with no buttons pressed
            self._timelines.record_frame(mx, my, False, False)
            self._fx_ghost.update()
            self._fx_player.update()
            self._render_tick = self._tick
            self._tick += 1
            if self._tick >= self._loop_frames:
                self._commit_and_start_next()
            return

        left_p = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT))
        right_p = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT))

        # Record THIS tick at the raw mouse position (teleports handled via offsets)
        self._timelines.record_frame(mx, my, left_p, right_p)

        # --- GHOST ACTIONS ---
        ghosts: List[GhostSample] = self._timelines.ghosts_for_frame(self._tick)
        while len(self._ghost_ctxs) < len(ghosts):
            self._ghost_ctxs.append(CursorCtx(room=self._player_ctx.room))

        for idx, g in enumerate(ghosts):
            ctx = self._ghost_ctxs[idx]
            gx = max(0, min(self._w - 1, int(g.x) + ctx.offset_x))
            gy = max(0, min(self._h - 1, int(g.y) + ctx.offset_y))

            # spawn ripple only if ghost is in the player's visible room
            if (g.left or g.right) and ctx.room == self._player_ctx.room:
                self._fx_ghost.add_click(gx, gy, int(g.color))

            if g.left:
                evt = self._level.interact("L", gx, gy, ctx.room)
                if evt is not None:
                    apply_event(ctx, evt, int(g.x), int(g.y))
            if g.right:
                evt = self._level.interact("R", gx, gy, ctx.room)
                if evt is not None:
                    apply_event(ctx, evt, int(g.x), int(g.y))

        # --- PLAYER ACTIONS ---
        # Effective position for interaction and drawing
        px_eff = max(0, min(self._w - 1, mx + self._player_ctx.offset_x))
        py_eff = max(0, min(self._h - 1, my + self._player_ctx.offset_y))
        self._mouse_eff_x, self._mouse_eff_y = px_eff, py_eff  # snapshot for draw()

        if left_p or right_p:
            self._fx_player.add_click(px_eff, py_eff, 7)
            if left_p:
                evt = self._level.interact("L", px_eff, py_eff, self._player_ctx.room)
                if evt is not None:
                    apply_event(self._player_ctx, evt, mx, my)
                    self._mouse_eff_x = max(
                        0, min(self._w - 1, mx + self._player_ctx.offset_x)
                    )
                    self._mouse_eff_y = max(
                        0, min(self._h - 1, my + self._player_ctx.offset_y)
                    )
            if right_p:
                evt = self._level.interact("R", px_eff, py_eff, self._player_ctx.room)
                if evt is not None:
                    apply_event(self._player_ctx, evt, mx, my)
                    self._mouse_eff_x = max(
                        0, min(self._w - 1, mx + self._player_ctx.offset_x)
                    )
                    self._mouse_eff_y = max(
                        0, min(self._h - 1, my + self._player_ctx.offset_y)
                    )

        # Effects update
        self._fx_ghost.update()
        self._fx_player.update()

        # Publish snapshot & advance
        self._render_tick = self._tick
        self._tick += 1
        if self._tick >= self._loop_frames:
            self._commit_and_start_next()

    def draw(self) -> None:
        pyxel.cls(1)  # background color 1

        # L2: objects (draw ONLY the player's current room)
        self._level.draw_room(self._player_ctx.room)

        # L3: previous mice clicks
        self._fx_ghost.draw()

        # L4: previous mice (only those in the same room as player)
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

        # L5: current mouse clicks
        self._fx_player.draw()

        # L6: current mouse — draw at EFFECTIVE position
        self._draw_pointer(
            int(self._mouse_eff_x), int(self._mouse_eff_y), int(7), int(0)
        )

        # L7: navigation bar (draw last so it's on top)
        self._draw_nav()
