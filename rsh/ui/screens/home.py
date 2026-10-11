from kivy.properties import StringProperty
from kivy.uix.screenmanager import Screen


class HomeScreen(Screen):
    # Shown under the title, e.g. "Listening..." or "Microphone permission denied".
    status_text = StringProperty("Starting...")
