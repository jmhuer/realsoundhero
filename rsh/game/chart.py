"""Charts: the list of notes a song asks you to play, and when.

Charts are stored as JSON files in the ``charts/`` folder, so you can write
new songs without touching code. See charts/twinkle_ukulele.json.
"""
import json
from dataclasses import dataclass
from typing import List, Optional

from rsh.dsp.notes import name_to_midi


@dataclass(frozen=True)
class NoteEvent:
    time: float  # seconds from the start of the song
    duration: float = 0.5  # seconds
    note: Optional[str] = None  # single note to play, e.g. "C4"
    chord: Optional[str] = None  # or a chord name from the instrument, e.g. "C"


@dataclass(frozen=True)
class Chart:
    title: str
    artist: str
    instrument: str  # instrument key, e.g. "ukulele"
    bpm: float
    notes: List[NoteEvent]

    @property
    def length(self) -> float:
        """Song length in seconds (end of the last note)."""
        return max((n.time + n.duration for n in self.notes), default=0.0)


def parse_chart(data: dict) -> Chart:
    """Build a Chart from already-loaded JSON data, checking it as we go."""
    notes = []
    for i, raw in enumerate(data["notes"]):
        event = NoteEvent(
            time=float(raw["time"]),
            duration=float(raw.get("duration", 0.5)),
            note=raw.get("note"),
            chord=raw.get("chord"),
        )
        if (event.note is None) == (event.chord is None):
            raise ValueError(f"note #{i}: give exactly one of 'note' or 'chord'")
        if event.note is not None:
            name_to_midi(event.note)  # raises ValueError if the note name is bad
        notes.append(event)
    notes.sort(key=lambda n: n.time)
    return Chart(
        title=data["title"],
        artist=data.get("artist", "Unknown"),
        instrument=data["instrument"],
        bpm=float(data.get("bpm", 120)),
        notes=notes,
    )


def load_chart(path: str) -> Chart:
    with open(path, encoding="utf-8") as f:
        return parse_chart(json.load(f))
