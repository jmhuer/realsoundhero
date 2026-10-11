"""The one safe crossing point between the audio thread and the Kivy (UI) thread.

Kivy widgets may only be changed from the main thread. The audio thread
therefore never touches the UI. It drops results into a queue, and a Kivy
``Clock`` timer on the main thread empties the queue ~30 times per second.

    audio thread:  bridge.push(reading)        (never waits)
    main thread:   Clock -> _drain -> on_readings([...])
"""
import queue
from typing import Callable, List, Optional

from kivy.clock import Clock

from rsh.events import PitchReading


class ReadingBridge:
    def __init__(self, max_items: int = 64):
        self._queue: "queue.Queue[PitchReading]" = queue.Queue(maxsize=max_items)
        self._event = None
        self._on_readings: Optional[Callable[[List[PitchReading]], None]] = None

    def push(self, reading: PitchReading) -> None:
        """Called from the audio thread. If the UI falls behind, the oldest item is dropped."""
        try:
            self._queue.put_nowait(reading)
        except queue.Full:
            try:
                self._queue.get_nowait()
            except queue.Empty:
                pass
            self._queue.put_nowait(reading)

    def start(self, on_readings: Callable[[List[PitchReading]], None], fps: float) -> None:
        """Start delivering batches of readings to ``on_readings`` on the main thread."""
        self._on_readings = on_readings
        if self._event is None:
            self._event = Clock.schedule_interval(self._drain, 1.0 / fps)

    def stop(self) -> None:
        if self._event is not None:
            self._event.cancel()
            self._event = None

    def _drain(self, _dt: float) -> None:
        readings = []
        while True:
            try:
                readings.append(self._queue.get_nowait())
            except queue.Empty:
                break
        if readings and self._on_readings is not None:
            self._on_readings(readings)
