"""Tuner screen: shows the note you're playing and how in-tune it is.

This is the first "real" screen. It proves the whole pipeline works:
mic -> audio thread -> analyzer -> bridge -> screen.
"""
from typing import List

from kivy.properties import ListProperty, NumericProperty, ObjectProperty, StringProperty
from kivy.uix.screenmanager import Screen

from rsh import config
from rsh.dsp.level import db_to_unit
from rsh.events import PitchReading

IN_TUNE_CENTS = 5.0
GREEN = (0.3, 0.85, 0.4, 1)
ORANGE = (1.0, 0.65, 0.2, 1)
GREY = (0.6, 0.6, 0.6, 1)


class TunerScreen(Screen):
    instrument = ObjectProperty(None)  # set by app.py

    level = NumericProperty(0.0)
    note_text = StringProperty("--")
    frequency_text = StringProperty("Play a note")
    cents_text = StringProperty("")
    string_text = StringProperty("")
    note_color = ListProperty(GREY)

    def on_readings(self, readings: List[PitchReading]) -> None:
        """Called by the app on the main thread with the newest batch of readings."""
        latest = readings[-1]
        self.level = db_to_unit(latest.level_db, config.METER_MIN_DB, config.METER_MAX_DB)

        if not latest.has_pitch:
            self.note_color = GREY
            return  # keep showing the last note so the display doesn't flicker

        self.note_text = latest.note_name
        self.frequency_text = f"{latest.frequency:.1f} Hz"
        self.cents_text = f"{latest.cents:+.0f} cents"
        self.note_color = GREEN if abs(latest.cents) <= IN_TUNE_CENTS else ORANGE

        if self.instrument is not None:
            index, note, cents = self.instrument.nearest_string(latest.frequency)
            string_number = len(self.instrument.open_strings) - index  # uke strings: 4 3 2 1
            self.string_text = f"Nearest string: {note} (string {string_number}) {cents:+.0f}c"
