"""A horizontal bar showing how loud the microphone is. The drawing lives in kv/widgets.kv."""
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget


class LevelMeter(Widget):
    # 0.0 = silent, 1.0 = maximum. Kivy redraws automatically when this changes.
    level = NumericProperty(0.0)
