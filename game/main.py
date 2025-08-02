from __future__ import annotations
import pyxel

WIDTH, HEIGHT = 160, 120
TITLE = "GMTK 2025"


class App:
    def __init__(self) -> None:
        pyxel.init(WIDTH, HEIGHT, title=TITLE)
        # Optional: load a .pyxres you make in game/assets
        # pyxel.load("game/assets/resources.pyxres")
        self.x, self.y = WIDTH // 2, HEIGHT // 2
        self.speed = 1

    # --- Update per frame ---
    def update(self) -> None:
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()

        dx = (pyxel.btn(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D)) - (
            pyxel.btn(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_A)
        )
        dy = (pyxel.btn(pyxel.KEY_DOWN) or pyxel.btn(pyxel.KEY_S)) - (
            pyxel.btn(pyxel.KEY_UP) or pyxel.btn(pyxel.KEY_W)
        )
        self.x = max(0, min(WIDTH - 8, self.x + dx * self.speed))
        self.y = max(0, min(HEIGHT - 8, self.y + dy * self.speed))

    # --- Draw when needed ---
    def draw(self) -> None:
        pyxel.cls(0)
        pyxel.rect(self.x, self.y, 8, 8, 11)
        pyxel.text(4, 4, "Move: Arrows/WASD   Quit: Q", 7)


def run() -> None:
    app = App()
    pyxel.run(app.update, app.draw)
