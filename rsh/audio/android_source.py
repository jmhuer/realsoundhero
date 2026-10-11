"""Microphone input on Android, using Android's own ``AudioRecord`` class.

``pyjnius`` lets Python call Java classes directly. ``autoclass`` loads a
Java class, and then we use it as if it were a Python class.

Android docs: https://developer.android.com/reference/android/media/AudioRecord

This module can only be imported on Android. factory.py takes care of that.
"""
from typing import Optional

import numpy as np
from jnius import autoclass

from rsh.audio.source import AudioSource

AudioRecord = autoclass("android.media.AudioRecord")
AudioFormat = autoclass("android.media.AudioFormat")
MediaRecorderAudioSource = autoclass("android.media.MediaRecorder$AudioSource")


class AndroidAudioSource(AudioSource):
    def _open(self) -> None:
        channel = AudioFormat.CHANNEL_IN_MONO
        encoding = AudioFormat.ENCODING_PCM_16BIT  # each sample = 2 bytes, -32768..32767

        min_bytes = AudioRecord.getMinBufferSize(self.sample_rate, channel, encoding)
        if min_bytes <= 0:
            raise RuntimeError(f"Sample rate {self.sample_rate} not supported (code {min_bytes})")
        # Give Android's internal buffer room for a few of our blocks so we never drop audio.
        internal_bytes = max(min_bytes, self.block_size * 2) * 4

        # VOICE_RECOGNITION asks Android to skip most of its "phone call" sound
        # processing (noise suppression, auto gain), which we don't want.
        self._record = AudioRecord(
            MediaRecorderAudioSource.VOICE_RECOGNITION,
            self.sample_rate,
            channel,
            encoding,
            internal_bytes,
        )
        if self._record.getState() != AudioRecord.STATE_INITIALIZED:
            self._record.release()
            raise RuntimeError("AudioRecord failed to start. Is the microphone permission granted?")

        # pyjnius copies Java's byte[] back into a Python bytearray after each read.
        self._buffer = bytearray(self.block_size * 2)
        self._record.startRecording()

    def _read_block(self) -> Optional[np.ndarray]:
        # read() waits ("blocks") until the buffer is full, about 46 ms for 2048 samples.
        n_bytes = self._record.read(self._buffer, 0, len(self._buffer))
        if n_bytes <= 0:
            return None
        pcm16 = np.frombuffer(bytes(self._buffer[:n_bytes]), dtype="<i2")
        return pcm16.astype(np.float32) / 32768.0  # scale to -1.0..1.0

    def _close(self) -> None:
        record = getattr(self, "_record", None)
        if record is not None:
            record.stop()
            record.release()
            self._record = None
