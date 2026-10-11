"""Pick the right AudioSource for wherever the app is running.

The rest of the app just calls ``create_audio_source()`` and never needs to
know whether it's on a phone, a laptop, or using fake audio.
"""
import logging
import os

from rsh.audio.source import AudioSource
from rsh.platform import IS_ANDROID

log = logging.getLogger(__name__)


def create_audio_source() -> AudioSource:
    if IS_ANDROID:
        from rsh.audio.android_source import AndroidAudioSource

        return AndroidAudioSource()

    from rsh.audio.desktop_source import (
        SineAudioSource,
        SoundDeviceAudioSource,
        has_microphone_support,
    )

    # Set RSH_FAKE_AUDIO=1 to force the fake sine-wave source.
    if os.environ.get("RSH_FAKE_AUDIO") != "1" and has_microphone_support():
        log.info("Audio: using desktop microphone (sounddevice)")
        return SoundDeviceAudioSource()
    log.info("Audio: using fake sine-wave source")
    return SineAudioSource()
