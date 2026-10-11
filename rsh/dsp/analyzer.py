"""The Analyzer turns each AudioBlock into a PitchReading.

It runs on the **audio thread**, so keep it fast and never touch the UI from
here.
"""
from typing import Callable, Optional

import numpy as np

from rsh import config
from rsh.dsp.level import rms, to_db
from rsh.dsp.notes import nearest_note
from rsh.dsp.pitch import detect_pitch
from rsh.events import AudioBlock, PitchReading

# Any function shaped like detect_pitch(samples, sample_rate, min_freq, max_freq).
PitchFunction = Callable[[np.ndarray, int, float, float], Optional[float]]


class Analyzer:
    def __init__(
        self,
        min_freq: float = config.MIN_FREQUENCY,
        max_freq: float = config.MAX_FREQUENCY,
        silence_db: float = config.SILENCE_DB,
        pitch_function: PitchFunction = detect_pitch,
    ):
        # The pitch function is passed in rather than hard-coded ("dependency
        # injection"), so tests or experiments can swap detectors easily.
        self.min_freq = min_freq
        self.max_freq = max_freq
        self.silence_db = silence_db
        self.pitch_function = pitch_function

    def process(self, block: AudioBlock) -> PitchReading:
        level_db = to_db(rms(block.samples))
        if level_db < self.silence_db:
            return PitchReading(time=block.time, level_db=level_db)

        hz = self.pitch_function(block.samples, block.sample_rate, self.min_freq, self.max_freq)
        if hz is None:
            return PitchReading(time=block.time, level_db=level_db)

        name, _midi, cents = nearest_note(hz)
        return PitchReading(
            time=block.time, level_db=level_db, frequency=hz, note_name=name, cents=cents
        )

    # TODO (Milestone 2): smooth readings over a few blocks (e.g. median of the
    #   last 3 frequencies) so the tuner display stops jittering.
    # TODO (Milestone 3): also run an OnsetDetector here (see dsp/onset.py).
