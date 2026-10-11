"""App-wide settings in one place.

Changing a number here changes it everywhere. Avoid sprinkling "magic
numbers" through the code.
"""

# --- Audio -----------------------------------------------------------------
# 44100 Hz is the one sample rate every Android device must support.
SAMPLE_RATE = 44100

# How many samples we analyse at a time. 2048 samples / 44100 Hz ~= 46 ms.
# Bigger = more accurate pitch but more delay. Smaller = faster but noisier.
BLOCK_SIZE = 2048

# --- Analysis --------------------------------------------------------------
# Only look for pitches in this range (Hz). Ukulele is roughly 260-1050 Hz;
# the wider range leaves room for low-G ukes, guitar and singing.
MIN_FREQUENCY = 80.0
MAX_FREQUENCY = 1500.0

# Anything quieter than this (in decibels, 0 dB = loudest possible) counts
# as silence, and we don't try to find a pitch in it.
SILENCE_DB = -55.0

# The level meter shows this range of decibels.
METER_MIN_DB = -70.0
METER_MAX_DB = 0.0

# --- UI --------------------------------------------------------------------
# How many times per second the screen pulls new results from the audio thread.
UI_FPS = 30

# The instrument used until we add an instrument-select screen.
DEFAULT_INSTRUMENT = "ukulele"
