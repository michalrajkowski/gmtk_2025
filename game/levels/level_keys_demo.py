# game/levels/level_keys_demo.py
from typing import Dict, List, Optional
import pyxel
from game.levels.level_base import LevelBase
from game.core.cursor import CursorEvent
from game.objects.base import LevelObject, Which, Action
from game.objects.pickable import Pickable, Key
from game.objects.key_wall import KeyWall
from game.objects.four_color_key_wall import FourColorKeyWall
from game.objects.locked_wall import LockedWall
from game.objects.button import Button
from game.objects.door import Door
from game.objects.flag import Flag

KEY_Y = 1
KEY_R = 2
KEY_G = 3
KEY_B = 4


class LevelKeysDemo(LevelBase):
    name: str = "Keys"
    difficulty: int = 2
    start_room: str = "A"
    max_cursors: int = 7
    loop_seconds: int = 30

    def __init__(self) -> None:
        # Rooms
        self._rooms: Dict[str, List[LevelObject]] = {
            "A": [],
            "B": [],
            "R1": [],
            "BLUE": [],
            "G1": [],
            "F": [],
        }

        # --- A: yellow key + yellow wall -> B ---
        self.key_y = Key(x=60, y=112, w=0, h=0, room_id="A", color=9, key_id=KEY_Y)
        self.wall_y = KeyWall(
            x=140, y=80, w=24, h=24, target_room="B", required_key=KEY_Y, wall_fill=9
        )
        self.wall_y.can_open = self._actor_has_key
        self._rooms["A"] = [self.wall_y]

        # --- B: RGB walls, red key on ground ---
        self.key_r = Key(x=60, y=112, w=0, h=0, room_id="B", color=8, key_id=KEY_R)
        self.wall_r = KeyWall(
            x=210, y=60, w=24, h=24, target_room="R1", required_key=KEY_R, wall_fill=8
        )
        self.wall_g = KeyWall(
            x=210, y=90, w=24, h=24, target_room="G1", required_key=KEY_G, wall_fill=11
        )
        self.wall_b = KeyWall(
            x=210,
            y=120,
            w=24,
            h=24,
            target_room="BLUE",
            required_key=KEY_B,
            wall_fill=12,
        )
        for w in (self.wall_r, self.wall_g, self.wall_b):
            w.can_open = self._actor_has_key
        self._rooms["B"] = [self.wall_r, self.wall_g, self.wall_b]

        # --- R1: blue key + door back to B ---
        self.key_b = Key(x=80, y=100, w=0, h=0, room_id="R1", color=12, key_id=KEY_B)
        self.door_r_back = Door(
            x=40, y=30, w=24, h=24, target_room="B", color=8, label="Back"
        )
        self._rooms["R1"] = [self.door_r_back]

        # --- BLUE: button + grey wall -> green key + door back to B ---
        self.btn_blue = Button(x=60, y=120, w=0, h=0, radius=10)
        self.grey_wall = LockedWall(
            x=140, y=80, w=24, h=24, is_open=False, fill=5, border=7, icon_col=7
        )
        self.key_g = Key(
            x=140, y=80, w=0, h=0, room_id="BLUE", color=11, key_id=KEY_G
        )  # initially behind wall
        self.door_b_back = Door(
            x=40, y=30, w=24, h=24, target_room="B", color=12, label="Back"
        )
        self._rooms["BLUE"] = [self.btn_blue, self.grey_wall, self.door_b_back]

        # --- G1: FourColorKeyWall -> F (+ optional back) ---
        self.fc_wall = FourColorKeyWall(
            x=140,
            y=80,
            w=32,
            h=32,
            target_room="F",
            key_y=KEY_Y,
            key_r=KEY_R,
            key_g=KEY_G,
            key_b=KEY_B,
        )
        self.fc_wall.can_open = self._actor_has_key
        self.door_g_back = Door(
            x=40, y=30, w=24, h=24, target_room="B", color=11, label="Back"
        )
        self._rooms["G1"] = [self.fc_wall, self.door_g_back]

        # --- F: flag ---
        # game/levels/level_keys_demo.py  (__init__)
        self.flag = Flag(x=150, y=80, w=24, h=24)
        self.flag.on_finish = self._finish
        self._rooms["F"] = [self.flag]  # <-- ensure it receives input

        # Global pickables
        self._pickables: List[Pickable] = [
            self.key_y,
            self.key_r,
            self.key_b,
            self.key_g,
        ]

        # --- add inside LevelKeysDemo.__init__ after building walls ---
        # Signatures of doors that KeyWalls spawn (per room)
        self._wall_door_sigs = {
            "A": {
                (
                    self.wall_y.x,
                    self.wall_y.y,
                    self.wall_y.w,
                    self.wall_y.h,
                    self.wall_y.target_room,
                )
            },
            "B": {
                (
                    self.wall_r.x,
                    self.wall_r.y,
                    self.wall_r.w,
                    self.wall_r.h,
                    self.wall_r.target_room,
                ),
                (
                    self.wall_g.x,
                    self.wall_g.y,
                    self.wall_g.w,
                    self.wall_g.h,
                    self.wall_g.target_room,
                ),
                (
                    self.wall_b.x,
                    self.wall_b.y,
                    self.wall_b.w,
                    self.wall_b.h,
                    self.wall_b.target_room,
                ),
            },
        }

    def _finish(self) -> None:
        self.completed = True

    # ===== helpers =====
    def _actor_has_key(self, actor_id: int, key_id: int) -> bool:
        for p in self._pickables:
            if isinstance(p, Key) and p.held_by == actor_id and p.key_id == key_id:
                return True
        return False

    def _held_by(self, actor_id: int) -> Optional[Pickable]:
        for p in self._pickables:
            if p.held_by == actor_id:
                return p
        return None

    def _grab_with_swap(self, actor_id: int, new_item: Pickable) -> None:
        old = self._held_by(actor_id)
        if old is not None and old is not new_item:
            old.held_by = None
            old.x, old.y = new_item.x, new_item.y
            old.room_id = new_item.room_id
        new_item.held_by = actor_id

    # ===== LevelBase =====
    def reset_level(self) -> None:
        self.completed = False
        for objs in self._rooms.values():
            for obj in objs:
                obj.reset()
        for p in self._pickables:
            p.reset()
        self._prune_spawned_doors()  # <-- remove any wall-spawned doors

    def on_loop_start(self) -> None:
        for objs in self._rooms.values():
            for obj in objs:
                obj.reset()
        for p in self._pickables:
            p.reset()
        self._prune_spawned_doors()  # <-- ensure new loop starts locked

    def set_active_actor(self, actor_id: int) -> None:
        super().set_active_actor(actor_id)
        # inform walls that depend on actor_id
        for objs in self._rooms.values():
            for obj in objs:
                if hasattr(obj, "set_active_actor"):
                    obj.set_active_actor(actor_id)  # type: ignore # KeyWall, FourColorKeyWall

    def on_actor_frame(self, actor_id: int, x: int, y: int, room_id: str) -> None:
        for p in self._pickables:
            p.on_actor_frame(actor_id, x, y, room_id)
        # BLUE room: button live control of the grey wall
        # (safe to set every frame)
        self.grey_wall.is_open = self.btn_blue.lit

    def interact(
        self, which: Which, action: Action, x: int, y: int, room_id: str
    ) -> Optional[CursorEvent]:
        # Update BLUE button each frame so .lit is accurate
        if room_id == "BLUE":
            self.btn_blue.handle_input(which, action, x, y)
            # wall opens only while held
            self.grey_wall.is_open = self.btn_blue.lit

        # 1) Let room objects handle/block first (so walls can absorb clicks)
        for obj in list(self._rooms.get(room_id, [])):
            spawned, evt = obj.handle_input(which, action, x, y)
            if evt is not None:
                return evt
            if spawned is not None:
                self._rooms[room_id].append(spawned)

        # 2) Pickup/steal with swap (only if click isn’t blocked by a closed plain wall)
        if action == "press":
            blocked = any(
                isinstance(o, LockedWall) and not o.is_open and o.contains(x, y)
                for o in self._rooms.get(room_id, [])
            )
            if not blocked:
                actor_id = getattr(self, "_active_actor_id", -999)
                for p in self._pickables:
                    if p.room_id == room_id and p.contains(x, y):
                        self._grab_with_swap(actor_id, p)
                        return None

        return None

    # --- add this helper method to LevelKeysDemo ---
    def _prune_spawned_doors(self) -> None:
        """Remove doors that were spawned by KeyWalls (so loops re-lock properly)."""
        for room_id, objs in list(self._rooms.items()):
            sigs = self._wall_door_sigs.get(room_id, set())
            if not sigs:
                continue
            # keep original 'back' doors (their signatures won't match the wall slots)
            self._rooms[room_id] = [
                o
                for o in objs
                if not (
                    isinstance(o, Door) and (o.x, o.y, o.w, o.h, o.target_room) in sigs
                )
            ]

    def draw_room(self, room_id: str) -> None:
        # Backgrounds: A dark, B normal, others slightly tinted for variety
        if room_id == "A":
            pyxel.cls(1)
        elif room_id == "B":
            pyxel.cls(10)  # “normal color”
        elif room_id == "R1":
            pyxel.cls(9)
        elif room_id == "BLUE":
            pyxel.cls(6)
        elif room_id == "G1":
            pyxel.cls(3)
        else:  # F
            pyxel.cls(2)

        # Draw room objects
        if room_id == "F":
            self.flag.draw()
        else:
            for obj in self._rooms.get(room_id, []):
                # In BLUE, draw wall after button so icon shows correctly
                obj.draw()

    # game/levels/level_keys_demo.py  (draw_room_overlay)
    def draw_room_overlay(self, room_id: str) -> None:
        for p in self._pickables:
            if p.room_id != room_id:
                continue
            # Hide the green key while the grey door is closed (and it isn’t held)
            if (
                p is self.key_g
                and room_id == "BLUE"
                and not self.grey_wall.is_open
                and p.held_by is None
            ):
                continue
            p.draw()
