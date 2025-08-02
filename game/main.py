# title: GMTK 2025 – Loop Mouse (demo)
# author: michalrajkowski
# desc: Time loop with multi-mouse-agents
# version: 0.3.1

from __future__ import annotations
from typing import Final, List

import pyxel

from game.levels.level_base import LevelBase
from game.levels.level_pads import LevelPads
from game.scenes.level_select import LevelEntry, LevelSelectScene
from game.scenes.gameplay import GameplayScene

WIDTH: Final[int] = 200
HEIGHT: Final[int] = 200
FPS: Final[int] = 30
LOOP_SECONDS: Final[int] = 20
TITLE: Final[str] = "Loop Mouse (Demo)"


def _draw_pointer(x: int, y: int, fill: int, outline: int) -> None:
    # --- YOUR WORKING SPRITE (unchanged logic) ---
    SQUARE_EDGE = 20
    x1, y1 = x + (SQUARE_EDGE * 0.25), y + int(SQUARE_EDGE * 0.75)
    x2, y2 = x, y
    x3, y3 = x + (SQUARE_EDGE * 0.75), y + (SQUARE_EDGE * 0.25)
    pyxel.tri(x1, y1, x2, y2, x3, y3, fill)
    pyxel.line(x1, y1, x2, y2, outline)
    pyxel.line(x2, y2, x3, y3, outline)
    pyxel.line(x3, y3, x1, y1, outline)
    # (tail stayed commented in your original)


class Game:
    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title=TITLE, fps=FPS)
        pyxel.mouse(False)

        self._entries: List[LevelEntry] = [
            LevelEntry(factory=LevelPads),
            # Add more levels here
        ]

        # Start on level select (now draws pointer and uses smaller squares)
        self._scene: object = LevelSelectScene(
            entries=self._entries,
            start_level=self._start_level,
            draw_pointer=_draw_pointer,  # <— pass pointer renderer
            width=WIDTH,
            height=HEIGHT,
        )

    # Called by LevelSelectScene
    def _start_level(self, level: LevelBase) -> None:
        self._scene = GameplayScene(
            level=level,
            draw_pointer=_draw_pointer,
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            loop_seconds=LOOP_SECONDS,
        )

    def update(self) -> None:
        getattr(self._scene, "update")()

    def draw(self) -> None:
        getattr(self._scene, "draw")()


def run() -> None:
    game = Game()
    pyxel.run(game.update, game.draw)


if __name__ == "__main__":
    run()
