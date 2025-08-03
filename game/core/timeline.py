from __future__ import annotations

from dataclasses import dataclass
from typing import Final, List, Optional, Tuple


@dataclass(frozen=True, slots=True)
class FrameRecord:
    x: int
    y: int
    left_p: bool
    right_p: bool
    left_h: bool
    right_h: bool


@dataclass(slots=True)
class GhostSample:
    x: int
    y: int
    left_p: bool
    right_p: bool
    left_h: bool
    right_h: bool
    color: int


class Timeline:
    def __init__(self, max_frames: int) -> None:
        self.max_frames: int = max_frames
        self.frames: List[FrameRecord] = []

    def record(
        self, x: int, y: int, left_p: bool, right_p: bool, left_h: bool, right_h: bool
    ) -> None:
        if len(self.frames) < self.max_frames:
            self.frames.append(FrameRecord(x, y, left_p, right_p, left_h, right_h))

    def sample(self, frame_index: int) -> Optional[FrameRecord]:
        if 0 <= frame_index < len(self.frames):
            return self.frames[frame_index]
        return None


TIMELINE = Timeline


class TimelineManager:
    _GHOST_COLORS: Final[tuple[int, ...]] = (12, 10, 11, 14, 8)

    def __init__(self, max_frames: int) -> None:
        self.max_frames: int = max_frames
        self.past_runs: List[TIMELINE] = []
        self._current: Optional[Timeline] = None
        self.player_pos: Tuple[int, int] = (80, 60)

    def start_run(self) -> None:
        self._current = Timeline(self.max_frames)

    def end_run(self) -> None:
        if self._current is not None:
            self.past_runs.append(self._current)
        self._current = None

    def discard_run(self) -> None:
        self._current = None

    def reset_all(self) -> None:
        self.past_runs.clear()
        self._current = None
        self.player_pos = (80, 60)

    def record_frame(
        self, x: int, y: int, left_p: bool, right_p: bool, left_h: bool, right_h: bool
    ) -> None:
        self.player_pos = (x, y)
        if self._current is not None:
            self._current.record(x, y, left_p, right_p, left_h, right_h)

    def ghosts_for_frame(self, frame_index: int) -> List[GhostSample]:
        """
        For each past run, return a GhostSample every frame.
        - While within the recorded run: replay inputs and position.
        - After the run ends: keep the ghost at its last position, with no inputs (idle).
        """
        samples: List[GhostSample] = []
        for idx, tl in enumerate(self.past_runs):
            if tl.frames:
                if 0 <= frame_index < len(tl.frames):
                    fr = tl.frames[frame_index]
                    left_p, right_p, left_h, right_h = (
                        fr.left_p,
                        fr.right_p,
                        fr.left_h,
                        fr.right_h,
                    )
                    x, y = fr.x, fr.y
                else:
                    # idle at final recorded position, no inputs
                    fr = tl.frames[-1]
                    x, y = fr.x, fr.y
                    left_p = right_p = left_h = right_h = False
            else:
                # empty timeline: park at last known player position, no inputs
                x, y = self.player_pos
                left_p = right_p = left_h = right_h = False

            color: int = self._GHOST_COLORS[idx % len(self._GHOST_COLORS)]
            samples.append(GhostSample(x, y, left_p, right_p, left_h, right_h, color))
        return samples
