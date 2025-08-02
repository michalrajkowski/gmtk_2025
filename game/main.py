# title: GMTK 2025 – Loop Mouse (demo)
# author: michalrajkowski
# desc: Time loop with multi-mouse-agents
# version: 0.2.1

from __future__ import annotations

from typing import Final

import pyxel

from game.core.timeline import GhostSample, TimelineManager
from game.levels.level_one import LevelOne

WIDTH: Final[int] = 160
HEIGHT: Final[int] = 120
FPS: Final[int] = 30
LOOP_SECONDS: Final[int] = 20
LOOP_FRAMES: Final[int] = LOOP_SECONDS * FPS
TITLE: Final[str] = "Loop Mouse (Demo)"


def _clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else hi - 1 if v >= hi else v


class Game:
    """ """

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title=TITLE, fps=FPS)
        pyxel.mouse(True)

        self.timelines: TimelineManager = TimelineManager(max_frames=LOOP_FRAMES)
        self.level: LevelOne = LevelOne()

        # Simulation tick we write/advance in update()
        self.tick: int = 0
        # Snapshot tick that draw() should render (set in update())
        self.render_tick: int = 0

        self._start_new_loop()

    # ---------------- Run lifecycle ----------------
    def _start_new_loop(self) -> None:
        self.level.on_loop_start()
        self.timelines.start_run()
        self.tick = 0
        self.render_tick = 0

    def _commit_and_start_next(self) -> None:
        self.timelines.end_run()
        self._start_new_loop()

    def _restart_discard_current(self) -> None:
        self.timelines.discard_run()
        self._start_new_loop()

    # ---------------- Update (simulation) ----------------
    def update(self) -> None:
        # Global controls
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
            return
        if pyxel.btnp(pyxel.KEY_RETURN):  # commit early
            self._commit_and_start_next()
            return
        if pyxel.btnp(pyxel.KEY_R):  # restart current loop (discard)
            self._restart_discard_current()
            return
        if pyxel.btnp(pyxel.KEY_N):  # reset level + timelines
            self.timelines.reset_all()
            self.level.reset_level()
            self._start_new_loop()
            return

        # --- 1) Read input for THIS tick ---
        px: int = _clamp(int(pyxel.mouse_x), 0, WIDTH)
        py: int = _clamp(int(pyxel.mouse_y), 0, HEIGHT)
        left_p: bool = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT))
        right_p: bool = bool(pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT))

        # --- 2) Record THIS tick ---
        self.timelines.record_frame(px, py, left_p, right_p)

        # --- 3) Apply actions for THIS tick ---
        # ghosts
        ghosts: list[GhostSample] = self.timelines.ghosts_for_frame(self.tick)
        for g in ghosts:
            if g.left:
                self.level.handle_left_click(int(g.x), int(g.y))
            if g.right:
                self.level.handle_right_click(int(g.x), int(g.y))
        # player
        if left_p:
            self.level.handle_left_click(px, py)
        if right_p:
            self.level.handle_right_click(px, py)

        # --- 4) Publish snapshot for draw() and advance simulation ---
        self.render_tick = self.tick  # draw will use this exact tick
        self.tick += 1

        # --- 5) Loop rollover ---
        if self.tick >= LOOP_FRAMES:
            self._commit_and_start_next()

    # ---------------- Draw (render only) ----------------
    def draw(self) -> None:
        pyxel.cls(0)

        # Level visuals
        self.level.draw()

        # Ghosts at the exact snapshot tick
        for g in self.timelines.ghosts_for_frame(self.render_tick):
            pyxel.circ(int(g.x), int(g.y), 2, g.color)

        # Current pointer marker (recorded position at snapshot tick)
        px, py = self.timelines.player_pos
        pyxel.rectb(px - 3, py - 3, 6, 6, 7)

        # HUD based on snapshot tick
        secs_left: float = max(0.0, LOOP_SECONDS - self.render_tick / FPS)
        pyxel.text(4, 4, f"Time: {secs_left:0.1f}s", 7)
        pyxel.text(4, 12, f"Loop #: {len(self.timelines.past_runs) + 1}", 6)
        pyxel.text(4, 20, "R=restart  Enter=commit  N=reset  Q=quit", 5)


def run() -> None:
    game = Game()
    pyxel.run(game.update, game.draw)


if __name__ == "__main__":
    run()
