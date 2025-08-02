from __future__ import annotations
from typing import Callable, Final

import pyxel


class LevelFinishedScene:
    def __init__(self, level_name: str, on_done: Callable[[], None]) -> None:
        self._name = level_name
        self._on_done = on_done
        self._timer = 0
        self._wait_frames: Final[int] = 60  # ~2 seconds at 30fps

    def update(self) -> None:
        self._timer += 1
        if (
            self._timer >= self._wait_frames
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            or pyxel.btnp(pyxel.KEY_RETURN)
        ):
            self._on_done()

    def draw(self) -> None:
        pyxel.cls(1)
        msg = f"Level '{self._name}' finished!"
        tw = len(msg) * 4
        pyxel.text((pyxel.width - tw) // 2, pyxel.height // 2 - 4, msg, 7)
        hint = "Click or Enter to continue"
        th = len(hint) * 4
        pyxel.text((pyxel.width - th) // 2, pyxel.height // 2 + 8, hint, 6)
