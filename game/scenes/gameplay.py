from __future__ import annotations
from typing import Callable, Final, List

import pyxel

from game.core.effects import Effects
from game.core.timeline import GhostSample, TimelineManager
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
        self._start_new_loop()

    # ----- lifecycle -----
    def _start_new_loop(self) -> None:
        self._level.on_loop_start()
        self._timelines.start_run()
        self._fx_ghost = Effects()
        self._fx_player = Effects()
        self._tick = 0
        self._render_tick = 0

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

        # Clamp input to window
        px = max(0, min(self._w - 1, int(pyxel.mouse_x)))
        py = max(0, min(self._h - 1, int(pyxel.mouse_y)))
        left_p = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT))
        right_p = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT))

        self._timelines.record_frame(px, py, left_p, right_p)

        ghosts: List[GhostSample] = self._timelines.ghosts_for_frame(self._tick)
        for g in ghosts:
            if g.left or g.right:
                self._fx_ghost.add_click(int(g.x), int(g.y), int(g.color))
            if g.left:
                self._level.handle_left_click(int(g.x), int(g.y))
            if g.right:
                self._level.handle_right_click(int(g.x), int(g.y))

        if left_p or right_p:
            self._fx_player.add_click(px, py, 7)
        if left_p:
            self._level.handle_left_click(px, py)
        if right_p:
            self._level.handle_right_click(px, py)

        self._fx_ghost.update()
        self._fx_player.update()

        self._render_tick = self._tick
        self._tick += 1
        if self._tick >= self._loop_frames:
            self._commit_and_start_next()

    def draw(self) -> None:
        pyxel.cls(1)  # background color 1

        # objects
        self._level.draw()

        # ghost clicks
        self._fx_ghost.draw()

        # ghosts
        for g in self._timelines.ghosts_for_frame(self._render_tick):
            self._draw_pointer(int(g.x), int(g.y), int(g.color), int(0))

        # player clicks
        self._fx_player.draw()

        # player
        px, py = self._timelines.player_pos
        self._draw_pointer(int(px), int(py), int(7), int(0))
