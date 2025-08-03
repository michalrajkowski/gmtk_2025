from __future__ import annotations
from typing import List, Optional, Tuple
import random
import math
import pyxel

from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import Which, Action


class Firework:
    """
    A single burst. Runtime state is only `frame`.
    Geometry/colors are precomputed constants; each draw() advances by 1 frame.
    """

    __slots__ = ("x", "y", "frame", "max_frames", "angles", "speeds", "r0", "base_col")

    def __init__(self, x: int, y: int) -> None:
        self.x, self.y = x, y
        self.frame = 0
        self.max_frames = random.randint(22, 34)

        # Static burst design
        n = random.randint(22, 36)
        self.angles = [
            (2.0 * math.pi * i / n) + random.uniform(-0.06, 0.06) for i in range(n)
        ]
        self.speeds = [random.uniform(1.2, 2.2) for _ in range(n)]  # px per frame
        self.r0 = random.randint(2, 3)  # initial particle radius (pixels)
        self.base_col = random.choice([7, 8, 9, 10, 11, 12, 13, 14])

    @property
    def alive(self) -> bool:
        return self.frame < self.max_frames

    def draw(self) -> None:
        """Draw snapshot at current frame, then advance exactly one frame."""
        if not self.alive:
            return

        t = self.frame / max(1, self.max_frames)  # 0..1
        # simple downward gravity curve for all sparks (constant per frame)
        gy = 0.04 * (self.frame * self.frame)

        # core flash for the first few frames
        if self.frame < 6:
            pyxel.circ(self.x, self.y, self.r0 + 1, self.base_col)

        # rings of sparks
        for theta, spd in zip(self.angles, self.speeds):
            r = spd * self.frame  # radial distance
            px = int(self.x + math.cos(theta) * r)
            py = int(self.y + math.sin(theta) * r + gy)
            # fade size over life
            pr = max(1, int(self.r0 * (1.0 - t)))
            # small color flicker: 70% base, else pick another bright color
            col = (
                self.base_col
                if random.random() < 0.7
                else random.choice([7, 8, 9, 10, 11, 12, 13, 14])
            )
            if 0 <= px < pyxel.width and 0 <= py < pyxel.height:
                pyxel.circ(px, py, pr, col)

        # advance one frame *per draw*
        self.frame += 1


class LevelBigButtonFireworks(LevelBase):
    """
    One room:
      - Giant circular button; each LEFT click increments a counter.
      - Every 5th click spawns a new Firework at a random screen position.
      - Multiple fireworks can exist concurrently.
      - Counter shows big ASCII digits (000..999); at 1000 you win.
      - Counter resets at the start of each loop.
    """

    name: str = "Fireworks"
    difficulty: int = 1
    start_room: str = "A"
    max_cursors: int = 99
    loop_seconds: int = 99

    DIGITS: dict[str, List[str]] = {
        "0": ["###", "#.#", "#.#", "#.#", "###"],
        "1": ["..#", "..#", "..#", "..#", "..#"],
        "2": ["###", "..#", "###", "#..", "###"],
        "3": ["###", "..#", "###", "..#", "###"],
        "4": ["#.#", "#.#", "###", "..#", "..#"],
        "5": ["###", "#..", "###", "..#", "###"],
        "6": ["###", "#..", "###", "#.#", "###"],
        "7": ["###", "..#", "..#", "..#", "..#"],
        "8": ["###", "#.#", "###", "#.#", "###"],
        "9": ["###", "#.#", "###", "..#", "###"],
    }

    def __init__(self) -> None:
        self._count: int = 0
        self._btn_center: Tuple[int, int] = (150, 135)
        self._btn_radius: int = 44
        self._btn_flash: int = 0

        self._fireworks: List[Firework] = []

    # --- LevelBase ---
    def reset_level(self) -> None:
        self.completed = False
        self._count = 0
        self._btn_flash = 0
        self._fireworks.clear()

    def on_loop_start(self) -> None:
        self._count = 0
        self._btn_flash = 0
        self._fireworks.clear()

    # --- helpers ---
    def _circ_contains(self, px: int, py: int, cx: int, cy: int, r: int) -> bool:
        dx, dy = px - cx, py - cy
        return dx * dx + dy * dy <= r * r

    def _spawn_firework_random(self) -> None:
        margin = 16
        x = random.randint(margin, pyxel.width - margin)
        y = random.randint(24 + margin, pyxel.height - margin)  # avoid top nav bar
        self._fireworks.append(Firework(x, y))

    def _draw_big_number(self, value: int, x: int, y: int, scale: int = 8) -> None:
        text = "1000" if value >= 1000 else f"{value:03d}"
        digit_w = 3 * scale
        gap = scale
        for idx, ch in enumerate(text):
            pat = self.DIGITS.get(ch, self.DIGITS["0"])
            ox = x + idx * (digit_w + gap)
            for j, row in enumerate(pat):
                for i, c in enumerate(row):
                    if c == "#":
                        px = ox + i * scale
                        py = y + j * scale
                        pyxel.rect(px, py, scale, scale, 7)

    # --- per-frame hooks ---
    def on_actor_frame(self, actor_id: int, x: int, y: int, room_id: str) -> None:
        # Button flash timer lives in update space; fireworks step during draw.
        if self._btn_flash > 0:
            self._btn_flash -= 1

    # --- input ---
    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        if room_id != "A":
            return None

        if which == "L" and action == "press":
            cx, cy = self._btn_center
            if self._circ_contains(x, y, cx, cy, self._btn_radius):
                self._count += 1
                self._btn_flash = 6
                if self._count % 5 == 0:
                    self._spawn_firework_random()
                if self._count >= 1000:
                    self.completed = True

        return None

    # --- rendering ---
    def draw_room(self, room_id: str) -> None:
        pyxel.cls(1)

        pyxel.text(10, 4, "", 6)

        # Counter centered
        scale = 8
        text = "1000" if self._count >= 1000 else f"{self._count:03d}"
        digits_w = len(text) * (3 * scale) + (len(text) - 1) * scale
        self._draw_big_number(
            self._count, x=(pyxel.width - digits_w) // 2, y=26, scale=scale
        )

        # Draw & advance ALL fireworks; keep only alive ones
        alive: List[Firework] = []
        for fw in self._fireworks:
            fw.draw()  # advances exactly one frame
            if fw.alive:
                alive.append(fw)
        self._fireworks = alive

        # Big button
        cx, cy = self._btn_center
        r = self._btn_radius
        fill = 11 if self._btn_flash > 0 else 8
        pyxel.circ(cx, cy, r, fill)
        pyxel.circb(cx, cy, r, 7)
        pyxel.text(cx - 18, cy - 3, "", 0)

    def draw_room_overlay(self, room_id: str) -> None:
        return None
