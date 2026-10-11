"""One play-through of one chart.  (Milestones 4-6)

The GameSession is the "referee". It owns the song clock, feeds incoming
readings to the Judge, and keeps score. The Play screen only *draws* what
the session tells it.
"""
from typing import List

from rsh.events import PitchReading
from rsh.game.chart import Chart, NoteEvent
from rsh.game.scoring import Judge, Judgement
from rsh.instruments.base import Instrument


class GameSession:
    def __init__(
        self,
        chart: Chart,
        instrument: Instrument,
        judge: Judge,
        latency_offset: float = 0.0,  # seconds, measured by the calibration screen (Milestone 6)
    ):
        self.chart = chart
        self.instrument = instrument
        self.judge = judge
        self.latency_offset = latency_offset
        self.judgements: List[Judgement] = []
        self.score = 0
        self.combo = 0

    def start(self, audio_time: float) -> None:
        """Remember the audio-clock time the song started at."""
        raise NotImplementedError("Milestone 4")

    def song_time(self, audio_time: float) -> float:
        """Convert an audio-clock time to song time (the clock the chart uses).

        Hint: audio_time - start_time - latency_offset
        """
        raise NotImplementedError("Milestone 4")

    def upcoming(self, audio_time: float, look_ahead: float = 3.0) -> List[NoteEvent]:
        """Notes the highway should draw: ones due in the next few seconds."""
        raise NotImplementedError("Milestone 4")

    def handle_readings(self, readings: List[PitchReading]) -> List[Judgement]:
        """Match readings (and later onsets) to expected notes and return new judgements.

        Notes that pass their window without a matching reading become MISS.
        """
        raise NotImplementedError("Milestone 5")

    @property
    def finished(self) -> bool:
        raise NotImplementedError("Milestone 5")
