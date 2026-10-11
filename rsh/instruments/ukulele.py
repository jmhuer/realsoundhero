"""Standard soprano/concert/tenor ukulele in GCEA tuning ("re-entrant").

"Re-entrant" means the G string (closest to your face) is *higher* than the
C string, so the lowest note is C4 (middle C), not G.

    String:  4th  3rd  2nd  1st
    Note:    G4   C4   E4   A4
    Hz:      392  262  330  440
"""
from rsh.instruments.base import Instrument

UKULELE = Instrument(
    key="ukulele",
    display_name="Ukulele (GCEA)",
    open_strings=("G4", "C4", "E4", "A4"),
    frets=15,
    chords={
        # Strings G C E A
        "C": (0, 0, 0, 3),
        "Am": (2, 0, 0, 0),
        "F": (2, 0, 1, 0),
        "G": (0, 2, 3, 2),
        # TODO: add more chords as songs need them (D, Em, G7, ...)
    },
)
