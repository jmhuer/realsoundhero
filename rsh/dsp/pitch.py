"""Pitch detection: "what note is being played?"

Right now we use the simplest method that works: take an FFT (which splits
sound into frequencies) and pick the loudest one.

Known weakness: real instruments play *harmonics* (2x, 3x, ... the note's
frequency) as well as the note itself. Sometimes a harmonic is louder than
the actual note, and then this detector reports the wrong octave. Fixing
that is Milestone 2 (YIN), see detect_pitch_yin below.
"""
from typing import Optional

import numpy as np


def detect_pitch_fft(
    samples: np.ndarray,
    sample_rate: int,
    min_freq: float = 80.0,
    max_freq: float = 1500.0,
) -> Optional[float]:
    """Return the strongest frequency (Hz) between min_freq and max_freq, or None."""
    n = len(samples)
    if n == 0:
        return None

    # 1. A "window" fades the block in and out so its edges don't add fake frequencies.
    windowed = samples * np.hanning(n)

    # 2. Zero-padding (making the FFT 4x longer) gives a finer frequency grid.
    n_fft = 4 * (1 << (n - 1).bit_length())
    spectrum = np.abs(np.fft.rfft(windowed, n_fft))
    bin_hz = sample_rate / n_fft

    # 3. Only search the frequency band we care about.
    lo = max(1, int(min_freq / bin_hz))
    hi = min(len(spectrum) - 2, int(max_freq / bin_hz))
    if hi <= lo:
        return None
    peak = lo + int(np.argmax(spectrum[lo:hi]))
    if spectrum[peak] <= 0:
        return None

    # 4. Parabolic interpolation: fit a curve through the peak and its two
    #    neighbours to land between FFT bins and get a more exact answer.
    a, b, c = np.log(spectrum[peak - 1 : peak + 2] + 1e-12)
    denom = a - 2 * b + c
    shift = 0.5 * (a - c) / denom if denom != 0 else 0.0
    shift = min(0.5, max(-0.5, shift))  # a true peak is never more than half a bin away
    hz = float((peak + shift) * bin_hz)

    # Noise often peaks right at the edge of the band. That's not a real note.
    if not (min_freq <= hz <= max_freq):
        return None
    return hz


def detect_pitch_yin(
    samples: np.ndarray,
    sample_rate: int,
    min_freq: float = 80.0,
    max_freq: float = 1500.0,
    threshold: float = 0.15,
) -> Optional[float]:
    """TODO (Milestone 2): implement the YIN pitch detector.

    YIN looks for how far the wave has to shift before it lines up with
    itself (its "period"). It is much better than the FFT peak at picking
    the right octave. Steps:

      1. Difference function d(tau) = sum((x[i] - x[i+tau])^2) for each lag
         tau. (Fast version: compute it with np.fft, see the paper.)
      2. Cumulative mean normalised difference d'(tau).
      3. Find the first tau where d'(tau) < threshold (absolute threshold).
      4. Parabolic interpolation around that tau.
      5. frequency = sample_rate / tau.

    Paper: de Cheveigne & Kawahara (2002), "YIN, a fundamental frequency
    estimator for speech and music".
    When it works: add tests in tests/test_pitch.py, then point
    ``detect_pitch`` below at this function.
    """
    raise NotImplementedError("YIN is Milestone 2, see the README TODO list")


# The detector the rest of the app uses. Swap it in one place when YIN is ready.
detect_pitch = detect_pitch_fft
