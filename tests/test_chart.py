import os

import pytest

from rsh.game.chart import load_chart, parse_chart

CHARTS = os.path.join(os.path.dirname(__file__), "..", "charts")


def test_load_sample_chart():
    chart = load_chart(os.path.join(CHARTS, "twinkle_ukulele.json"))
    assert chart.instrument == "ukulele"
    assert chart.notes[0].note == "C4"
    assert chart.length > 10
    times = [n.time for n in chart.notes]
    assert times == sorted(times)


def test_note_needs_note_or_chord():
    with pytest.raises(ValueError):
        parse_chart({"title": "x", "instrument": "ukulele", "notes": [{"time": 1.0}]})
