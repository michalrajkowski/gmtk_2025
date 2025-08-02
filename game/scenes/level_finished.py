from __future__ import annotations
from typing import Callable, Final, List
import random
import math
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
        # physics: gravity + mild drag for a pleasing arc
        self.vy += 0.08  # gravity (pull down)
        self.vx *= 0.995  # slight drag
        self.vy *= 0.995

        self.x += self.vx
        self.y += self.vy

        self.age += 1
        return self.age < self.max_age

    def draw(self) -> None:
        # shrink over life; switch to pixel at the end for sparkle
        t = self.age / self.max_age
        r = max(1, int(self.radius * (1.0 - t)))
        ix, iy = int(self.x), int(self.y)
        if 0 <= ix < pyxel.width and 0 <= iy < pyxel.height:
            if r <= 1:
                pyxel.pset(ix, iy, self.color)
            else:
                pyxel.circ(ix, iy, r, self.color)


class LevelFinishedScene:
    def __init__(self, level_name: str, on_done: Callable[[], None]) -> None:
        self._name = level_name
        self._on_done = on_done
        self._timer = 0
        self._wait_frames: Final[int] = 600  # ~2s at 30fps

        self._parts: List[_Particle] = []
        self._spawn_cooldown = 0

    def _spawn_firework(self) -> None:
        # Pick a random center (keep away from edges a bit)
        cx = random.randint(24, pyxel.width - 24)
        cy = random.randint(28, pyxel.height - 24)

        # Base parameters
        n = random.randint(22, 36)  # number of spokes
        base_speed = random.uniform(1.3, 2.4)  # initial radial speed
        max_age = random.randint(22, 34)  # particle lifetime
        radius0 = random.randint(2, 4)  # initial draw radius
        palette = [7, 8, 9, 10, 11, 12, 13, 14]
        base_color = random.choice(palette)

        # Create a circular ring of particles with slight jitter
        for i in range(n):
            theta = (2.0 * math.pi * i / n) + random.uniform(-0.06, 0.06)
            spd = base_speed * random.uniform(0.9, 1.1)
            vx = spd * math.cos(theta)
            vy = spd * math.sin(theta)
            color = base_color if random.random() < 0.7 else random.choice(palette)
            pr = radius0 if random.random() < 0.75 else max(1, radius0 - 1)
            self._parts.append(_Particle(cx, cy, vx, vy, color, max_age, pr))

        # Core flash: short-lived bright puff at the center
        flash_color = random.choice(palette)
        for _ in range(6):
            self._parts.append(_Particle(cx, cy, 0.0, 0.0, flash_color, 8, radius0 + 1))

        # Next burst after a short random delay
        self._spawn_cooldown = random.randint(8, 14)

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

        # fireworks behind text
        for p in self._parts:
            p.draw()

        msg = f"Level '{self._name}' finished!"
        tw = len(msg) * 4
        pyxel.text((pyxel.width - tw) // 2, pyxel.height // 2 - 4, msg, 7)

        hint = "Click or Enter to continue"
        th = len(hint) * 4
        pyxel.text((pyxel.width - th) // 2, pyxel.height // 2 + 8, hint, 6)
