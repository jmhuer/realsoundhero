"""The Kivy App: the "composition root" where every piece gets created and connected.

Nothing else in the code creates the big objects (audio source, analyzer,
screens). It all happens here, so this is the one place to read to see
how the app fits together:

    AudioSource ──(audio thread)──> Analyzer ──> ReadingBridge ──(main thread)──> current Screen
"""
import logging
import os
from typing import List

from kivy.app import App
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from rsh import config
from rsh.audio.factory import create_audio_source
from rsh.dsp.analyzer import Analyzer
from rsh.events import AudioBlock, PitchReading
from rsh.instruments import get_instrument
from rsh.platform.permissions import request_microphone_permission
from rsh.ui.bridge import ReadingBridge
from rsh.ui.screens.home import HomeScreen
from rsh.ui.screens.play import PlayScreen
from rsh.ui.screens.tuner import TunerScreen
from rsh.ui.widgets.level_meter import LevelMeter  # noqa: F401  (registers the widget for kv)

log = logging.getLogger(__name__)
KV_DIR = os.path.join(os.path.dirname(__file__), "ui", "kv")
ANDROID_BACK_KEY = 27  # Kivy reports the Android back button as the Escape key


class RealSoundHeroApp(App):
    title = "RealSoundHero"

    def build(self):
        Window.clearcolor = (0.08, 0.08, 0.11, 1)
        Window.bind(on_keyboard=self._on_keyboard)
        for kv_file in ("widgets.kv", "screens.kv"):
            Builder.load_file(os.path.join(KV_DIR, kv_file))

        # --- Create the pieces ---
        self.instrument = get_instrument(config.DEFAULT_INSTRUMENT)
        self.analyzer = Analyzer()
        self.bridge = ReadingBridge()
        self.audio = create_audio_source()
        self.mic_allowed = False

        # --- Build the screens ---
        self.screens = ScreenManager(transition=SlideTransition(duration=0.2))
        self.screens.add_widget(HomeScreen(name="home"))
        self.screens.add_widget(TunerScreen(name="tuner", instrument=self.instrument))
        self.screens.add_widget(PlayScreen(name="play", instrument=self.instrument))
        return self.screens

    # --- App lifecycle (Kivy calls these) ------------------------------------

    def on_start(self):
        request_microphone_permission(self._on_permission_result)

    def on_pause(self):
        # The phone went to the home screen. Release the mic so other apps can use it.
        self.stop_listening()
        return True  # True = "please resume me later" rather than closing the app

    def on_resume(self):
        if self.mic_allowed:
            self.start_listening()

    def on_stop(self):
        self.stop_listening()

    # --- Microphone ----------------------------------------------------------

    @mainthread  # Android answers on its own thread, so hop back to Kivy's
    def _on_permission_result(self, granted: bool) -> None:
        self.mic_allowed = granted
        if granted:
            self.start_listening()
        else:
            self._set_status("Microphone permission denied. Enable it in Settings.")

    def start_listening(self) -> None:
        try:
            self.audio.start(self._on_audio_block)
        except Exception as exc:
            log.exception("Could not start audio")
            self._set_status(f"Mic error: {exc}")
            return
        self.bridge.start(self._on_readings, config.UI_FPS)
        self._set_status("Listening...")
        Clock.unschedule(self._check_audio_health)
        Clock.schedule_interval(self._check_audio_health, 1.0)

    def stop_listening(self) -> None:
        Clock.unschedule(self._check_audio_health)
        self.bridge.stop()
        self.audio.stop()

    def _check_audio_health(self, _dt) -> None:
        if self.audio.error is not None:
            self._set_status(f"Audio error: {self.audio.error!r} (see adb logcat)")

    def _on_audio_block(self, block: AudioBlock) -> None:
        """Runs on the AUDIO thread. Analyse, then hand off. Never touch widgets here!"""
        self.bridge.push(self.analyzer.process(block))

    def _on_readings(self, readings: List[PitchReading]) -> None:
        """Runs on the MAIN thread. Send results to whichever screen is showing."""
        screen = self.screens.current_screen
        if hasattr(screen, "on_readings"):
            screen.on_readings(readings)

    # --- Navigation ----------------------------------------------------------

    def go_to(self, screen_name: str) -> None:
        going_back = screen_name == "home"
        self.screens.transition.direction = "right" if going_back else "left"
        self.screens.current = screen_name

    def _on_keyboard(self, _window, key, *_args):
        if key == ANDROID_BACK_KEY and self.screens.current != "home":
            self.go_to("home")
            return True  # handled. Don't let Kivy close the app.
        return False

    def _set_status(self, text: str) -> None:
        self.screens.get_screen("home").status_text = text
