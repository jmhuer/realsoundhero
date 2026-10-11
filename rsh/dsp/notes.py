"""Music math: convert between frequency (Hz), MIDI numbers and note names.

MIDI numbers give every piano key a whole number: A4 (440 Hz) = 69,
middle C (C4) = 60. Each step of +1 is one semitone (one fret on a uke).
"""
import math
import re
from typing import Tuple

NOTE_NAMES = ("C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B")
A4_HZ = 440.0
A4_MIDI = 69

_NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d+)$")
_FLATS = {"Db": "C#", "Eb": "D#", "Gb": "F#", "Ab": "G#", "Bb": "A#"}


def hz_to_midi(hz: float) -> float:
    """440.0 -> 69.0. The result has a fractional part when the pitch is between notes."""
    if hz <= 0:
        raise ValueError("frequency must be positive")
    return A4_MIDI + 12.0 * math.log2(hz / A4_HZ)


def midi_to_hz(midi: float) -> float:
    """69 -> 440.0"""
    return A4_HZ * 2.0 ** ((midi - A4_MIDI) / 12.0)


def midi_to_name(midi: int) -> str:
    """69 -> 'A4', 60 -> 'C4'"""
    octave = midi // 12 - 1
    return f"{NOTE_NAMES[midi % 12]}{octave}"


def name_to_midi(name: str) -> int:
    """'A4' -> 69, 'C#4' -> 61, 'Bb3' -> 58"""
    match = _NOTE_RE.match(name.strip())
    if not match:
        raise ValueError(f"not a note name: {name!r}")
    letter, accidental, octave = match.groups()
    pitch = letter.upper() + accidental
    pitch = _FLATS.get(pitch, pitch)
    if pitch not in NOTE_NAMES:  # e.g. "Cb" or "E#"
        raise ValueError(f"unsupported note name: {name!r}")
    return (int(octave) + 1) * 12 + NOTE_NAMES.index(pitch)


def name_to_hz(name: str) -> float:
    """'A4' -> 440.0"""
    return midi_to_hz(name_to_midi(name))


def cents_between(hz: float, reference_hz: float) -> float:
    """How far hz is from reference_hz in cents (100 cents = 1 semitone)."""
    return 1200.0 * math.log2(hz / reference_hz)


def nearest_note(hz: float) -> Tuple[str, int, float]:
    """Find the closest note to a frequency.

    Returns (name, midi, cents). Example: 445 Hz -> ('A4', 69, +19.6), meaning
    "A4, but 19.6 cents sharp".
    """
    midi = int(round(hz_to_midi(hz)))
    return midi_to_name(midi), midi, cents_between(hz, midi_to_hz(midi))
