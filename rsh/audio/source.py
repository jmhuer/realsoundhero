"""The base class every audio source shares.

It runs a background thread that keeps reading blocks of audio and passes
each one to a callback. Subclasses only fill in three small methods:

    _open()        get the microphone ready
    _read_block()  wait for the next block_size samples, return them as float32
    _close()       release the microphone

This pattern (the base class owns the loop, subclasses fill in the steps)
is called the "template method" pattern.

Threads in one sentence: the audio loop must never wait for the screen,
and the screen must never wait for the audio, so they run side by side.
"""
import logging
import threading
from abc import ABC, abstractmethod
from typing import Callable, Optional

import numpy as np

from rsh import config
from rsh.events import AudioBlock

log = logging.getLogger(__name__)

BlockCallback = Callable[[AudioBlock], None]


class AudioSource(ABC):
    def __init__(self, sample_rate: int = config.SAMPLE_RATE, block_size: int = config.BLOCK_SIZE):
        self.sample_rate = sample_rate
        self.block_size = block_size
        self._on_block: Optional[BlockCallback] = None
        self._running = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self.error: Optional[Exception] = None  # set if the audio thread crashed

    @property
    def is_running(self) -> bool:
        return self._running.is_set()

    def start(self, on_block: BlockCallback) -> None:
        """Start listening. ``on_block`` is called **on the audio thread** for every block."""
        if self._thread is not None:
            return
        self._on_block = on_block
        self.error = None
        self._open()
        self._running.set()
        self._thread = threading.Thread(target=self._run, name="audio", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._running.clear()
        self._thread.join(timeout=1.0)  # let the current read finish before closing
        self._thread = None
        self._close()

    def _run(self) -> None:
        position = 0  # total samples read so far: our steady audio clock
        try:
            while self._running.is_set():
                samples = self._read_block()
                if samples is None or len(samples) == 0:
                    continue
                block = AudioBlock(samples, self.sample_rate, position)
                position += len(samples)
                try:
                    self._on_block(block)
                except Exception as exc:
                    # A bug while *analysing* one block shouldn't stop the microphone.
                    # Remember it (the UI shows it) and keep listening.
                    if self.error is None:
                        log.exception("Error while processing an audio block")
                    self.error = exc
        except Exception as exc:  # the microphone itself failed: report it and stop
            log.exception("Audio thread crashed")
            self.error = exc
            self._running.clear()

    @abstractmethod
    def _open(self) -> None: ...

    @abstractmethod
    def _read_block(self) -> Optional[np.ndarray]: ...

    @abstractmethod
    def _close(self) -> None: ...
