# 🎸 RealSoundHero

**Guitar Hero, but with a real instrument.** The phone listens through its microphone to you playing a real ukulele (other instruments later), works out which notes you play and when, and scores you against a song chart in real time.

Built with **Python + [Kivy](https://kivy.org)** and packaged for Android with **Buildozer**. This is a learning project, so the code is organised to teach clean, modular design as it grows.

> **Status: skeleton (v0.1).** The app runs on Android, asks for the microphone, and has a working **Tuner** screen that shows the loudness, the note you're playing, and how in-tune it is. The game itself is laid out as stubs plus a step-by-step [TODO roadmap](#todo-roadmap).

---

## Quick start

New to all this? Follow **[docs/SETUP.md](docs/SETUP.md)**. It explains every step.

```bash
# 1. Desktop (fast iteration)
/usr/bin/python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest                          # run the tests
python main.py                  # run the app (RSH_FAKE_AUDIO=1 for a fake ukulele)

# 2. Android phone (USB debugging on, plugged in)
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
buildozer -v android debug deploy run logcat
```

---

## How the code is organised

```
main.py                 ← entry point (tiny)
buildozer.spec          ← Android build settings
rsh/
├── app.py              ← creates & connects everything ("composition root")
├── config.py           ← all tunable numbers in one place
├── events.py           ← data passed between layers (AudioBlock, PitchReading)
├── audio/              ← 👂 get sound: Android mic, laptop mic, or fake
├── dsp/                ← 🧠 turn sound into numbers: level, pitch, (onsets, chords)
├── instruments/        ← 🎸 tunings & chord shapes; ukulele.py, registry.py
├── game/               ← 📏 rules: chart.py, scoring.py, session.py
├── platform/           ← 📱 Android-only helpers (mic permission)
└── ui/                 ← 🖼️ Kivy screens, widgets, .kv layouts
charts/                 ← songs as JSON (twinkle_ukulele.json)
tests/                  ← pytest tests (run on your laptop)
docs/                   ← SETUP, ARCHITECTURE, LEARNING_PATH
```

The one rule to remember: **`dsp/`, `instruments/` and `game/` never import Kivy or Android.** They're plain Python + numpy, which is why they can be tested in under a second on a laptop. Read **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** for the full design: data flow, threads, the audio clock, and the patterns used.

```
Mic ─▶ AudioSource (audio thread) ─▶ Analyzer ─▶ ReadingBridge (queue) ─▶ Screen (Kivy thread)
                                                                          └─▶ GameSession ─▶ Judge  (later)
```

---

## TODO roadmap

Work top to bottom. Each item says *where* the code goes. [docs/LEARNING_PATH.md](docs/LEARNING_PATH.md) explains *what you'll learn* in each one. Tick boxes as you go!

### ✅ Milestone 1: Skeleton
- [x] Project structure, layered packages, tests
- [x] Android build with Buildozer (mic permission, numpy)
- [x] Live mic capture on Android (`rsh/audio/android_source.py`)
- [x] Desktop mic + fake audio source (`rsh/audio/desktop_source.py`)
- [x] Basic FFT pitch detection + Tuner screen

### Milestone 2: Accurate tuner
- [ ] Implement YIN in `rsh/dsp/pitch.py` → `detect_pitch_yin()`, then set `detect_pitch = detect_pitch_yin`
- [ ] Make `test_strong_second_harmonic` pass (remove `xfail` in `tests/test_pitch.py`)
- [ ] Smooth readings (median of last 3) in `rsh/dsp/analyzer.py`
- [ ] Add a confidence value to `PitchReading`. Ignore low-confidence pitches.
      (On the phone, room noise like fans currently shows up as low notes, ~90 Hz.)
- [ ] Measure the real noise floor on the phone and tune `SILENCE_DB` in `rsh/config.py`
- [ ] Draw a needle/arrow for cents (flat ◀ ▶ sharp) on the Tuner

### Milestone 3: Onset (pluck/strum) detection
- [ ] Implement `OnsetDetector` in `rsh/dsp/onset.py` (spectral flux)
- [ ] Add an `Onset` event in `rsh/events.py`, and push onsets through the bridge
- [ ] Tests with synthetic "pluck" signals (a sine with a sharp attack, then decay)

### Milestone 4: Note highway (Play screen)
- [ ] `GameSession.start / song_time / upcoming` in `rsh/game/session.py` (+ tests)
- [ ] Draw lanes (one per string) and falling notes in `rsh/ui/screens/play.py`
- [ ] Load `charts/twinkle_ukulele.json` and add a 3-2-1 countdown

### Milestone 5: Scoring
- [ ] Implement `Judge.judge()` in `rsh/game/scoring.py` (remove `skip` in `tests/test_scoring.py`)
- [ ] `GameSession.handle_readings()`: match readings and onsets to notes, mark misses
- [ ] Show score, combo, and Perfect/Good/Miss pop-ups

### Milestone 6: Latency calibration
- [ ] Calibration screen: click track, the player plucks along, measure the average offset
- [ ] Save the offset with `JsonStore` and pass it to `GameSession(latency_offset=...)`

### Milestone 7: Chords
- [ ] `chroma_vector()` and `chord_match()` in `rsh/dsp/chroma.py` (+ tests)
- [ ] Support `"chord": "C"` events in the game
- [ ] Add more ukulele chord shapes in `rsh/instruments/ukulele.py`

### Milestone 8: Real-app polish
- [ ] Song select screen (lists `charts/*.json`) and results screen
- [ ] High scores with `kivy.storage.jsonstore.JsonStore`
- [ ] App icon + splash screen (`icon.filename`, `presplash.filename` in buildozer.spec)
- [ ] Settings screen (difficulty = hit window sizes, low-G uke toggle)

### Milestone 9: More instruments
- [ ] `rsh/instruments/guitar.py` (E2 A2 D3 G3 B3 E4) + register it in `registry.py`
- [ ] Instrument select screen. Charts declare which instrument they're for.
- [ ] Check that nothing in `dsp/` or `game/` assumed "ukulele"

### Milestone 10: Performance
- [ ] Time `Analyzer.process()` on the phone. It must stay well under 46 ms.
- [ ] If needed, try the `aubio` python-for-android recipe for pitch and onsets

### Stretch goals
- [ ] Play a backing track in sync with the chart
- [ ] Import charts from MIDI files, or build a simple chart editor
- [ ] GitHub Actions workflow that builds the APK on every push

---

## Is Kivy the right choice?

**Yes, for learning and for this kind of game.** The research behind the design:

- **Microphone:** Android's `AudioRecord` via `pyjnius` gives raw samples in Python.
  - `plyer` can only record to a file.
  - The old `audiostream` library is unmaintained.
- **Maths:** `numpy` builds for Android through python-for-android. `scipy` doesn't, so stick to numpy.
- **Speed:** analysing a 2048-sample block takes a few milliseconds.
  - Total delay from pluck to app is roughly 40–80 ms.
  - That's fine for scoring with calibration. It's not fine for playing the sound back live.
- **If you ever outgrow it:** the logic in `dsp/` and `game/` carries over to Godot or native Android (Kotlin + Oboe). Measure first!

## Tested toolchain

| Tool | Version |
|---|---|
| Host OS | Ubuntu 22.04, Python 3.10 (system, in a venv) |
| Java | OpenJDK 17 |
| Buildozer | 1.6.0 |
| python-for-android | `develop` @ `d97d8071` (pinned in buildozer.spec, builds Python 3.14 for the phone) |
| Android NDK / API | r28c / target 35, min 24 (downloaded by buildozer) |
| Kivy (desktop) | 2.3.1 |
| Phone | Pixel 9a, Android 16 (API 36) |

## Ukulele reference

Standard GCEA tuning ("re-entrant": the G string is *higher* than the C string):

| String | 4th | 3rd | 2nd | 1st |
|---|---|---|---|---|
| Note | G4 | C4 | E4 | A4 |
| Frequency | 392.00 Hz | 261.63 Hz | 329.63 Hz | 440.00 Hz |
