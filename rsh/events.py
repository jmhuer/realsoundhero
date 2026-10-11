"""The "messages" that flow through the app.

Each layer talks to the next by passing one of these small, read-only
(``frozen``) dataclasses. Because they never change after they're created,
it's safe to hand them from the audio thread to the UI thread.

    AudioSource --AudioBlock--> Analyzer --PitchReading--> UI / Game
"""
from dataclasses import dataclass
from typing import Optional

import numpy as np


@dataclass(frozen=True)
class AudioBlock:
    """A short chunk of microphone audio."""

    samples: np.ndarray  # mono float32 samples between -1.0 and 1.0
    sample_rate: int  # samples per second, e.g. 44100
    start_sample: int  # position of samples[0], counted from when recording started

    @property
    def time(self) -> float:
        """Start time of this block in seconds, measured by the audio clock.

        We use the sample count instead of the computer's clock because
        it's perfectly steady. That matters later for scoring.
        """
        return self.start_sample / self.sample_rate


@dataclass(frozen=True)
class PitchReading:
    """What the analyzer heard in one AudioBlock."""

    time: float  # seconds, same clock as AudioBlock.time
    level_db: float  # loudness in decibels (0 = max, -60 = very quiet)
    frequency: Optional[float] = None  # Hz, or None if silent or no clear pitch
    note_name: Optional[str] = None  # e.g. "A4"
    cents: Optional[float] = None  # how far off the note: -50..+50 (100 cents = 1 semitone)

    @property
    def has_pitch(self) -> bool:
        return self.frequency is not None


# TODO (Milestone 3): add an ``Onset`` event (time, strength) for strums/plucks.
# TODO (Milestone 5): add a ``Judgement`` event, or reuse rsh.game.scoring.Judgement.
