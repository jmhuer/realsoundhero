"""Test pitch detection with synthetic (computer-made) sounds whose answer we know."""
import numpy as np
import pytest

from rsh.dsp.analyzer import Analyzer
from rsh.dsp.level import rms, to_db
from rsh.dsp.pitch import detect_pitch
from rsh.events import AudioBlock

SR = 44100
N = 2048


def tone(freq, harmonics=(1.0,), amplitude=0.3):
    t = np.arange(N) / SR
    wave = sum(a * np.sin(2 * np.pi * freq * (i + 1) * t) for i, a in enumerate(harmonics))
    return (amplitude * wave).astype(np.float32)


@pytest.mark.parametrize("freq", [261.63, 329.63, 392.00, 440.00, 880.00])
def test_pure_tones(freq):
    assert detect_pitch(tone(freq), SR) == pytest.approx(freq, abs=3.0)


def test_tone_with_weaker_harmonics():
    assert detect_pitch(tone(440.0, harmonics=(1.0, 0.5, 0.25)), SR) == pytest.approx(440, abs=3)


@pytest.mark.xfail(reason="FFT-peak picks the loudest harmonic. Fixed by YIN (Milestone 2)")
def test_strong_second_harmonic():
    # Real strings often have a louder 2nd harmonic. A good detector still says 261.63.
    assert detect_pitch(tone(261.63, harmonics=(0.4, 1.0)), SR) == pytest.approx(261.63, abs=3)


def test_noise_never_gives_impossible_pitch():
    # Regression test: on the phone, real mic noise once produced a negative
    # frequency and crashed the audio thread.
    rng = np.random.default_rng(0)
    for _ in range(200):
        hz = detect_pitch(rng.standard_normal(N).astype(np.float32), SR, 80.0, 1500.0)
        assert hz is None or 80.0 <= hz <= 1500.0


def test_tone_below_band_is_ignored():
    assert detect_pitch(tone(60.0), SR, 80.0, 1500.0) is None


def test_level():
    assert rms(np.zeros(N, dtype=np.float32)) == 0.0
    assert to_db(1.0) == 0.0
    assert to_db(0.1) == pytest.approx(-20.0)


def test_analyzer_silence_and_note():
    analyzer = Analyzer()
    silent = analyzer.process(AudioBlock(np.zeros(N, dtype=np.float32), SR, 0))
    assert not silent.has_pitch

    reading = analyzer.process(AudioBlock(tone(440.0), SR, SR))
    assert reading.note_name == "A4"
    assert reading.time == pytest.approx(1.0)
