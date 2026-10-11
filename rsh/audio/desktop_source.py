"""Audio sources for developing on a laptop.

* ``SoundDeviceAudioSource`` uses your computer's microphone
  (needs ``pip install sounddevice``).
* ``SineAudioSource`` invents sound: it cycles through the four ukulele
  strings, one per second. That way the app works even with no microphone,
  and you can check the tuner gives the right answers.
"""
import time
from typing import Optional

import numpy as np

from rsh.audio.source import AudioSource

try:
    import sounddevice
except Exception:  # not installed, or no audio system available
    sounddevice = None


class SoundDeviceAudioSource(AudioSource):
    def _open(self) -> None:
        self._stream = sounddevice.InputStream(
            samplerate=self.sample_rate, channels=1, dtype="float32", blocksize=self.block_size
        )
        self._stream.start()

    def _read_block(self) -> Optional[np.ndarray]:
        data, _overflowed = self._stream.read(self.block_size)
        return data[:, 0].copy()

    def _close(self) -> None:
        self._stream.stop()
        self._stream.close()


class SineAudioSource(AudioSource):
    NOTES_HZ = (392.00, 261.63, 329.63, 440.00)  # G4 C4 E4 A4: ukulele open strings

    def _open(self) -> None:
        self._phase = 0.0
        self._sample_count = 0
        self._rng = np.random.default_rng()

    def _read_block(self) -> Optional[np.ndarray]:
        seconds = self._sample_count // self.sample_rate
        freq = self.NOTES_HZ[seconds % len(self.NOTES_HZ)]

        # Keep the wave continuous between blocks by carrying the phase over.
        step = 2 * np.pi * freq / self.sample_rate
        phases = self._phase + step * np.arange(self.block_size)
        self._phase = float((phases[-1] + step) % (2 * np.pi))
        self._sample_count += self.block_size

        # The note plus a quieter 2nd harmonic and a little noise, which is a bit like a real string.
        wave = 0.3 * np.sin(phases) + 0.1 * np.sin(2 * phases)
        wave += 0.005 * self._rng.standard_normal(self.block_size)

        time.sleep(self.block_size / self.sample_rate)  # pretend to be real-time
        return wave.astype(np.float32)

    def _close(self) -> None:
        pass


def has_microphone_support() -> bool:
    if sounddevice is None:
        return False
    try:
        return sounddevice.query_devices(kind="input") is not None
    except Exception:
        return False
