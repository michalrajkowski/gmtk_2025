from __future__ import annotations
from typing import Callable, Final, List

import pyxel

from game.core.effects import Effects
from game.core.timeline import GhostSample, TimelineManager
from game.core.cursor import CursorCtx, apply_event
from game.levels.level_base import LevelBase


class GameplayScene:
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

        # Back button (if you use exit_to_menu)
        self._back_x, self._back_y, self._back_w, self._back_h = 4, 4, 16, 16

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

    # ----- update/draw -----
    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            return
        if self._exit_to_menu and pyxel.btnp(pyxel.KEY_ESCAPE):
            self._exit_to_menu()
            return
        if pyxel.btnp(pyxel.KEY_RETURN):
            self._commit_and_start_next()
            return
        if pyxel.btnp(pyxel.KEY_R):
            self._restart_discard_current()
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

        # Back button click (optional)
        if self._exit_to_menu and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            if (
                self._back_x <= mx < self._back_x + self._back_w
                and self._back_y <= my < self._back_y + self._back_h
            ):
                self._exit_to_menu()
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
                    # refresh effective snapshot in case of teleport
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

        # L6: current mouse — draw at EFFECTIVE position (matches where clicks land)
        self._draw_pointer(
            int(self._mouse_eff_x), int(self._mouse_eff_y), int(7), int(0)
        )

        # Back button UI (only if a handler was provided)
        if self._exit_to_menu:
            pyxel.rect(self._back_x, self._back_y, self._back_w, self._back_h, 0)
            pyxel.rectb(self._back_x, self._back_y, self._back_w, self._back_h, 7)
            pyxel.text(self._back_x + 4, self._back_y + 5, "<", 7)
