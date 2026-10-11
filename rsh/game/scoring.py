"""Scoring: compare what the chart expected with what the player did.  (Milestone 5)

The Judge only answers "how good was this one hit?". Keeping it small and
free of Kivy makes it easy to test. tests/test_scoring.py already holds the
tests it has to pass. Remove their ``skip`` marks when you start.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Optional

from rsh.game.chart import NoteEvent


class Grade(Enum):
    PERFECT = "Perfect"
    GOOD = "Good"
    MISS = "Miss"


@dataclass(frozen=True)
class HitWindows:
    """How close in time (seconds, either side) a hit must be for each grade."""

    perfect: float = 0.06
    good: float = 0.14


@dataclass(frozen=True)
class Judgement:
    event: NoteEvent
    grade: Grade
    offset: Optional[float] = None  # seconds early (-) or late (+). None for a miss.


class Judge:
    def __init__(self, windows: HitWindows = HitWindows()):
        self.windows = windows

    def judge(
        self, expected: NoteEvent, played_time: Optional[float], played_note: Optional[str]
    ) -> Judgement:
        """Grade one expected note.

        TODO (Milestone 5):
          * No hit (played_time is None) or the wrong note -> MISS
          * offset = played_time - expected.time
          * abs(offset) <= windows.perfect -> PERFECT
          * abs(offset) <= windows.good    -> GOOD
          * otherwise -> MISS
          Later: decide whether to allow octave mistakes (C5 for C4) on easy mode.
        """
        raise NotImplementedError("Scoring is Milestone 5, see the README TODO list")
