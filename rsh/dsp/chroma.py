"""Chord detection with chroma vectors.  (Milestone 7)

A chroma vector has 12 numbers, one per pitch class (C, C#, D, ... B). Each
says how much of that note is in the sound, ignoring octave.

Big idea: the game already knows which chord the chart expects. So we never
have to ask the hard question "what chord is this?". We only ask the easy
one: "does this sound like a C major chord?"

Suggested approach:
  1. Take an FFT of a longer block (4096+ samples, chords need detail).
  2. For every FFT bin between ~100 and ~2000 Hz, find its pitch class with
     rsh.dsp.notes.hz_to_midi(freq) % 12 and add the bin's magnitude there.
  3. Normalise the 12 numbers so they sum to 1.
  4. Compare with a chord template, e.g. C major = C, E, G = {0, 4, 7},
     using cosine similarity. A score above ~0.7 is probably a match.
"""
from typing import Iterable

import numpy as np


def chroma_vector(samples: np.ndarray, sample_rate: int) -> np.ndarray:
    """Return a length-12 array of pitch-class energy (C first)."""
    raise NotImplementedError("Chord detection is Milestone 7, see the README TODO list")


def chord_match(chroma: np.ndarray, pitch_classes: Iterable[int]) -> float:
    """Score 0..1 for how well ``chroma`` matches a chord, e.g. pitch_classes={0, 4, 7}."""
    raise NotImplementedError("Chord detection is Milestone 7, see the README TODO list")
