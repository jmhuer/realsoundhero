"""Onset detection: "when was a string plucked or strummed?"  (Milestone 3)

A rhythm game cares about *when* you play as much as *what* you play. An
onset is the moment a new note starts.

Suggested approach, spectral flux:
  1. For each block, compute the magnitude spectrum: np.abs(np.fft.rfft(...)).
  2. flux = sum of the *increases* in each frequency bin since the last block:
         np.sum(np.maximum(0, spectrum - previous_spectrum))
  3. An onset happens when flux jumps well above its recent average (keep a
     short history and compare against mean + k * std).
  4. Ignore new onsets for ~50 ms after one fires (a "refractory period").

Tip: blocks of 2048 samples are ~46 ms apart, which is too coarse for
timing. Analyse smaller hops (e.g. 512 samples) inside each block, or
lower config.BLOCK_SIZE once YIN is in place.
"""
from typing import Optional

from rsh.events import AudioBlock


class OnsetDetector:
    def __init__(self, sensitivity: float = 1.5):
        self.sensitivity = sensitivity

    def process(self, block: AudioBlock) -> Optional[float]:
        """Return the onset time in seconds if this block contains one, else None."""
        raise NotImplementedError("Onset detection is Milestone 3, see the README TODO list")
