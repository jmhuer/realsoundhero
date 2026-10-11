"""RealSoundHero: a rhythm game you play with a real instrument.

Package layout (see docs/ARCHITECTURE.md for the full story):

    audio/        "ears"   - get raw sound from the microphone
    dsp/          "brain"  - turn sound into numbers (loudness, pitch, ...)
    instruments/  facts about each instrument (tuning, chords)
    game/         rules    - charts, scoring, the song clock
    platform/     Android-only helpers (permissions)
    ui/           Kivy screens and widgets - only *shows* things

Rule of thumb: dsp/, instruments/ and game/ never import Kivy or Android,
so you can test them on your laptop with plain ``pytest``.
"""

__version__ = "0.1.0"
