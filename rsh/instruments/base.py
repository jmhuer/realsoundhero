"""What every instrument looks like to the rest of the app.

An instrument is just *data*: its strings, how many frets it has, and some
chord shapes. Adding a guitar later means writing one new file like
ukulele.py. No other code has to change.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from rsh.dsp.notes import cents_between, midi_to_hz, midi_to_name, name_to_hz, name_to_midi


@dataclass(frozen=True)
class Instrument:
    key: str  # short id used in code and chart files, e.g. "ukulele"
    display_name: str  # shown to the player, e.g. "Ukulele (GCEA)"
    open_strings: Tuple[str, ...]  # note of each open string, in the order you name them
    frets: int  # how many frets the neck has
    # chord name -> fret for each string (same order as open_strings). 0 = open, -1 = not played.
    chords: Dict[str, Tuple[int, ...]] = field(default_factory=dict)

    def string_frequencies(self) -> List[float]:
        return [name_to_hz(n) for n in self.open_strings]

    def note_range(self) -> Tuple[float, float]:
        """Lowest and highest playable frequency in Hz."""
        midis = [name_to_midi(n) for n in self.open_strings]
        return midi_to_hz(min(midis)), midi_to_hz(max(midis) + self.frets)

    def nearest_string(self, hz: float) -> Tuple[int, str, float]:
        """Which open string is this pitch closest to? Returns (index, note, cents).

        Handy for a tuner. Example: 438 Hz on a ukulele -> (3, 'A4', -7.9).
        """
        best = min(
            range(len(self.open_strings)),
            key=lambda i: abs(cents_between(hz, name_to_hz(self.open_strings[i]))),
        )
        note = self.open_strings[best]
        return best, note, cents_between(hz, name_to_hz(note))

    def chord_notes(self, chord: str) -> List[str]:
        """Note names sounding in a chord shape, e.g. ukulele 'C' -> ['G4', 'C4', 'E4', 'C5']."""
        shape = self.chords[chord]
        return [
            midi_to_name(name_to_midi(open_note) + fret)
            for open_note, fret in zip(self.open_strings, shape)
            if fret >= 0
        ]
