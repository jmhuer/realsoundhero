import pytest

from rsh.instruments import get_instrument


def test_ukulele_strings():
    uke = get_instrument("ukulele")
    assert uke.string_frequencies() == pytest.approx([392.00, 261.63, 329.63, 440.00], abs=0.01)


def test_ukulele_range():
    low, high = get_instrument("ukulele").note_range()
    assert low == pytest.approx(261.63, abs=0.01)  # C4: re-entrant tuning, so G4 isn't lowest
    assert high == pytest.approx(1046.5, abs=0.1)  # A4 + 15 frets = C6


def test_nearest_string():
    index, note, cents = get_instrument("ukulele").nearest_string(438.0)
    assert (index, note) == (3, "A4")
    assert cents < 0  # flat


def test_chord_notes():
    assert get_instrument("ukulele").chord_notes("C") == ["G4", "C4", "E4", "C5"]


def test_unknown_instrument():
    with pytest.raises(KeyError):
        get_instrument("theremin")
