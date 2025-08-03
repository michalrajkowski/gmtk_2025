from __future__ import annotations
from typing import Final, Dict
import pyxel

from game.levels.level_base import LevelBase
from game.levels.level_flag_only import LevelFlagOnly
from game.levels.level_pads import LevelPads
from game.levels.level_rooms_demo import LevelRoomsDemo
from game.scenes.level_select import LevelEntry, LevelSelectScene
from game.scenes.gameplay import GameplayScene
from game.scenes.level_finished import LevelFinishedScene
from game.levels.level_switch_lock import LevelSwitchLock
from game.levels.level_button_lock import LevelButtonLock
from game.levels.level_four_hold_lock import LevelFourHoldLock
from game.levels.level_first_room_button import LevelFirstRoomButton
from game.levels.level_door_maze import LevelDoorMaze


WIDTH: Final[int] = 300
HEIGHT: Final[int] = 200
FPS: Final[int] = 30
LOOP_SECONDS: Final[int] = 20
TITLE: Final[str] = "Loop Mouse (Demo)"


def _draw_pointer(x: int, y: int, fill: int, outline: int) -> None:
    SQUARE_EDGE = 20
    x1, y1 = x + (SQUARE_EDGE * 0.25), y + int(SQUARE_EDGE * 0.75)
    x2, y2 = x, y
    x3, y3 = x + (SQUARE_EDGE * 0.75), y + (SQUARE_EDGE * 0.25)
    pyxel.tri(x1, y1, x2, y2, x3, y3, fill)
    pyxel.line(x1, y1, x2, y2, outline)
    pyxel.line(x2, y2, x3, y3, outline)
    pyxel.line(x3, y3, x1, y1, outline)


class Game:
    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title=TITLE, fps=FPS)
        pyxel.mouse(False)

        self._entries = [
            LevelEntry(factory=LevelFlagOnly),
            LevelEntry(factory=LevelSwitchLock),
            LevelEntry(factory=LevelButtonLock),
            LevelEntry(factory=LevelFourHoldLock),
            LevelEntry(factory=LevelFirstRoomButton),
            LevelEntry(factory=LevelDoorMaze),
            LevelEntry(factory=LevelPads),
            LevelEntry(factory=LevelRoomsDemo),
        ]
        self._completed: Dict[str, bool] = {}
        self._show_menu()

    def _is_completed(self, name: str) -> bool:
        return self._completed.get(name, False)

    def _mark_completed_and_finish(self, level_name: str) -> None:
        self._completed[level_name] = True
        # show "level finished" screen, then return to menu
        self._scene = LevelFinishedScene(level_name, on_done=self._show_menu)

    def _show_menu(self) -> None:
        self._scene = LevelSelectScene(
            entries=self._entries,
            start_level=self._start_level,  # type: ignore
            draw_pointer=_draw_pointer,
            width=WIDTH,
            height=HEIGHT,
            is_completed=self._is_completed,
        )

    def _start_level(self, level: LevelBase) -> None:
        # Reset the level when entering from menu
        level.reset_level()
        self._scene = GameplayScene(
            level=level,
            draw_pointer=_draw_pointer,
            width=WIDTH,
            height=HEIGHT,
            fps=FPS,
            loop_seconds=getattr(level, "loop_seconds", LOOP_SECONDS),
            exit_to_menu=self._show_menu,
            on_level_completed=self._mark_completed_and_finish,
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
