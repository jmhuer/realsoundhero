import pytest

from rsh.dsp.notes import hz_to_midi, midi_to_name, name_to_hz, name_to_midi, nearest_note


def test_a4_is_440():
    assert hz_to_midi(440.0) == pytest.approx(69)
    assert name_to_hz("A4") == pytest.approx(440.0)


@pytest.mark.parametrize(
    "name, midi", [("C4", 60), ("C#4", 61), ("Db4", 61), ("G4", 67), ("A4", 69), ("C5", 72)]
)
def test_name_to_midi(name, midi):
    assert name_to_midi(name) == midi


def test_midi_to_name_round_trip():
    for midi in range(36, 96):
        assert name_to_midi(midi_to_name(midi)) == midi


def test_nearest_note_reports_cents():
    name, midi, cents = nearest_note(445.0)
    assert (name, midi) == ("A4", 69)
    assert cents == pytest.approx(19.56, abs=0.1)


def test_bad_note_name():
    with pytest.raises(ValueError):
        name_to_midi("H2")
