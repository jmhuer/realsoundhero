"""Loudness helpers."""
import math

import numpy as np


def rms(samples: np.ndarray) -> float:
    """Root-mean-square: the average "energy" of a block of samples (0.0 to 1.0)."""
    if len(samples) == 0:
        return 0.0
    return float(np.sqrt(np.mean(np.square(samples, dtype=np.float64))))


def to_db(value: float, floor_db: float = -100.0) -> float:
    """Convert a 0..1 amplitude to decibels. 1.0 -> 0 dB, 0.1 -> -20 dB, 0.01 -> -40 dB."""
    if value <= 0.0:
        return floor_db
    return max(floor_db, 20.0 * math.log10(value))


def db_to_unit(db: float, min_db: float, max_db: float) -> float:
    """Map decibels onto 0..1, which is handy for drawing a meter."""
    if max_db <= min_db:
        raise ValueError("max_db must be greater than min_db")
    return min(1.0, max(0.0, (db - min_db) / (max_db - min_db)))
