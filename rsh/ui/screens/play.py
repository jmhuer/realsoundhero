"""Play screen: the actual game.  (Milestones 4-5)

TODO (Milestone 4), the "note highway":
  * Load a chart: rsh.game.chart.load_chart("charts/twinkle_ukulele.json")
  * Create a GameSession (rsh/game/session.py)
  * Every frame (Clock.schedule_interval), ask the session for upcoming
    notes and draw them as rectangles falling toward a "hit line".
    Draw on ``self.canvas`` with kivy.graphics Color/Rectangle, or use one
    small Widget per note.
  * One lane per ukulele string (4 lanes). Use the instrument to work out
    which string a note belongs on.

TODO (Milestone 5):
  * In on_readings(), pass readings to session.handle_readings() and flash
    "Perfect!/Good/Miss" for each Judgement returned.
  * Show score and combo labels.
"""
from typing import List

from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from rsh.events import PitchReading


class PlayScreen(Screen):
    instrument = ObjectProperty(None)  # set by app.py

    def on_readings(self, readings: List[PitchReading]) -> None:
        pass  # TODO (Milestone 5): forward to the GameSession
