from __future__ import annotations
from typing import Callable, Final, List
import random
import pyxel


class _Particle:
    __slots__ = ("x", "y", "vx", "vy", "age", "max_age", "color", "radius")

    def __init__(
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        color: int,
        max_age: int,
        radius: int,
    ) -> None:
        self.x, self.y = x, y
        self.vx, self.vy = vx, vy
        self.age = 0
        self.max_age = max_age
        self.color = color
        self.radius = radius

    def update(self) -> bool:
        # simple physics
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.05  # gravity
        self.age += 1
        return self.age < self.max_age

    def draw(self) -> None:
        # fade radius over time
        r = max(1, int(self.radius * (1.0 - self.age / self.max_age)))
        if r <= 1:
            if 0 <= int(self.x) < pyxel.width and 0 <= int(self.y) < pyxel.height:
                pyxel.pset(int(self.x), int(self.y), self.color)
        else:
            pyxel.circ(int(self.x), int(self.y), r, self.color)


class LevelFinishedScene:
    def __init__(self, level_name: str, on_done: Callable[[], None]) -> None:
        self._name = level_name
        self._on_done = on_done
        self._timer = 0
        self._wait_frames: Final[int] = 60  # ~2s at 30fps

        self._parts: List[_Particle] = []
        self._spawn_cooldown = 0

    def _spawn_firework(self) -> None:
        # random position with some top margin (avoid nav overlap if any)
        x = random.randint(20, pyxel.width - 20)
        y = random.randint(24, pyxel.height - 20)

        # choose a bright color palette
        base_colors = [7, 8, 9, 10, 11, 12, 13, 14]
        color = random.choice(base_colors)

        count = random.randint(22, 36)
        speed = random.uniform(1.0, 2.6)
        max_age = random.randint(20, 36)
        radius0 = random.randint(2, 4)

        for i in range(count):
            ang = random.uniform(0, 6.28318)
            spd = speed * random.uniform(0.6, 1.2)
            vx = spd * pyxel.cos(ang)
            vy = spd * pyxel.sin(ang) * -1  # bias upward a bit
            c = color if random.random() < 0.75 else random.choice(base_colors)
            r = radius0 if random.random() < 0.7 else max(1, radius0 - 1)
            self._parts.append(_Particle(x, y, vx, vy, c, max_age, r))

        # schedule next burst
        self._spawn_cooldown = random.randint(6, 14)

    def update(self) -> None:
        self._timer += 1

        # spawn fireworks periodically
        if self._spawn_cooldown <= 0:
            self._spawn_firework()
        else:
            self._spawn_cooldown -= 1

        # update particles
        self._parts = [p for p in self._parts if p.update()]

        # exit
        if (
            self._timer >= self._wait_frames
            or pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)
            or pyxel.btnp(pyxel.KEY_RETURN)
        ):
            self._on_done()

    def draw(self) -> None:
        pyxel.cls(1)
        for p in self._parts:
            p.draw()

        msg = f"Level '{self._name}' finished!"
        tw = len(msg) * 4
        pyxel.text((pyxel.width - tw) // 2, pyxel.height // 2 - 4, msg, 7)

        hint = "Click or Enter to continue"
        th = len(hint) * 4
        pyxel.text((pyxel.width - th) // 2, pyxel.height // 2 + 8, hint, 6)
