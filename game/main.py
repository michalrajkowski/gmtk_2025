# title: GMTK 2025 – Loop Mouse (demo)
# author: michalrajkowski
# desc: Time loop with multi-mouse-agents
# version: 0.2.1

from __future__ import annotations

from typing import Final

import pyxel

from game.core.timeline import GhostSample, TimelineManager
from game.core.effects import Effects
from game.levels.level_pads import LevelPads

WIDTH: Final[int] = 200
HEIGHT: Final[int] = 200
FPS: Final[int] = 30
LOOP_SECONDS: Final[int] = 20
LOOP_FRAMES: Final[int] = LOOP_SECONDS * FPS
TITLE: Final[str] = "Loop Mouse (Demo)"

GHOST_COLORS: Final[tuple[int, ...]] = (12, 10, 11, 14, 8)


def _clamp(v: int, lo: int, hi: int) -> int:
    return lo if v < lo else hi - 1 if v >= hi else v


def _draw_pointer(x: int, y: int, fill: int, outline: int) -> None:
    """
    Draw a tilted cursor-like pointer:
      - triangular head (tip at x,y)
      - small tail rectangle
      - black outline
    Coordinates are relative to the tip.
    """
    SQUARE_EDGE = 20
    # Triangle vertices (tilted up-right look):
    x1, y1 = x + (SQUARE_EDGE * 0.25), y + int(SQUARE_EDGE * 0.75)
    x2, y2 = x, y
    x3, y3 = x + (SQUARE_EDGE * 0.75), y + (SQUARE_EDGE * 0.25)

    # Fill head (requires Pyxel >=2.x with tri)
    pyxel.tri(x1, y1, x2, y2, x3, y3, fill)
    # Outline with lines
    pyxel.line(x1, y1, x2, y2, outline)
    pyxel.line(x2, y2, x3, y3, outline)
    pyxel.line(x3, y3, x1, y1, outline)

    # # # Tail (small rectangle near base)
    # tx, ty, tw, th = x - 6, y + 8, 6, 8
    # pyxel.rect(tx, ty, tw, th, fill)
    # pyxel.rectb(tx, ty, tw, th, outline)


class Game:
    """
    update(): advances simulation, records/replays, spawns effects, sets render snapshot.
    draw(): background effects -> level -> ghosts -> current pointer (no mutation).
    """

    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title=TITLE, fps=FPS)
        pyxel.mouse(False)  # hide OS cursor; we render our own

        self.timelines: TimelineManager = TimelineManager(max_frames=LOOP_FRAMES)
        self.level: LevelPads = LevelPads()

        self.fx_ghost: Effects = Effects()  # previous mice clicks
        self.fx_player: Effects = Effects()  # current mouse clicks

        self.tick: int = 0
        self.render_tick: int = 0
        self._start_new_loop()

    # ---------------- Run lifecycle ----------------
    def _start_new_loop(self) -> None:
        self.level.on_loop_start()
        self.timelines.start_run()

        self.fx_ghost = Effects()
        self.fx_player = Effects()

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
            if g.left or g.right:
                self.fx_ghost.add_click(int(g.x), int(g.y), g.color)
            if g.left:
                self.level.handle_left_click(int(g.x), int(g.y))
            if g.right:
                self.level.handle_right_click(int(g.x), int(g.y))

        # Player (and spawn player click ripples)
        if left_p or right_p:
            self.fx_player.add_click(px, py, 7)  # white ripple for player
        if left_p:
            self.level.handle_left_click(px, py)
        if right_p:
            self.level.handle_right_click(px, py)

        # 4) Effects update
        self.fx_ghost.update()
        self.fx_player.update()

        # 5) Publish snapshot & advance
        self.render_tick = self.tick
        self.tick += 1

        # 6) Loop rollover
        if self.tick >= LOOP_FRAMES:
            self._commit_and_start_next()

    # ---------------- Draw (render only) ----------------
    def draw(self) -> None:
        pyxel.cls(0)

        # -------- LAYER 1: background (none yet) --------
        # (Draw parallax, tiles, etc. here later.)

        # -------- LAYER 2: objects (level) --------
        self.level.draw()

        # -------- LAYER 3: previous mice clicks (ghost ripples) --------
        self.fx_ghost.draw()

        # -------- LAYER 4: previous mice (ghost pointers) --------
        for g in self.timelines.ghosts_for_frame(self.render_tick):
            _draw_pointer(int(g.x), int(g.y), fill=g.color, outline=0)

        # -------- LAYER 5: current mouse clicks (player ripples) --------
        self.fx_player.draw()

        # -------- LAYER 6: current mouse (pointer) --------
        px, py = self.timelines.player_pos
        _draw_pointer(px, py, fill=7, outline=0)

        # HUD based on snapshot tick
        secs_left: float = max(0.0, LOOP_SECONDS - self.render_tick / FPS)
        pyxel.text(2, 2, f"Time: {secs_left:0.1f}s", 7)
        pyxel.text(4, 12, f"Loop #: {len(self.timelines.past_runs) + 1}", 6)
        pyxel.text(4, 20, "R=restart  Enter=commit  N=reset  Q=quit", 5)


def run() -> None:
    game = Game()
    pyxel.run(game.update, game.draw)


if __name__ == "__main__":
    run()
