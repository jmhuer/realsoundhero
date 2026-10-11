"""Tests for Milestone 5. They describe what the Judge *should* do.

Remove the ``skip`` line, run ``pytest``, and make them pass. This is
"test-driven development".
"""
import pytest

from rsh.game.chart import NoteEvent
from rsh.game.scoring import Grade, Judge

pytestmark = pytest.mark.skip(reason="TODO Milestone 5: implement Judge.judge()")

EXPECTED = NoteEvent(time=10.0, note="C4")


def test_perfect():
    assert Judge().judge(EXPECTED, 10.02, "C4").grade is Grade.PERFECT


def test_good_when_a_bit_late():
    j = Judge().judge(EXPECTED, 10.10, "C4")
    assert j.grade is Grade.GOOD
    assert j.offset == pytest.approx(0.10)


def test_miss_when_too_late():
    assert Judge().judge(EXPECTED, 10.5, "C4").grade is Grade.MISS


def test_miss_wrong_note():
    assert Judge().judge(EXPECTED, 10.0, "D4").grade is Grade.MISS


def test_miss_nothing_played():
    assert Judge().judge(EXPECTED, None, None).grade is Grade.MISS
