# Architecture

This document explains **how the code is organised and why**. Read it before adding features. If you understand the five ideas below, you'll know where any new piece of code should go.

---

## 1. The big picture

```
 ┌───────────┐  AudioBlock   ┌──────────┐ PitchReading ┌──────────────┐   list of     ┌──────────────┐
 │  audio/   │ ────────────▶ │  dsp/    │ ───────────▶ │ ui/bridge.py │ ────────────▶ │ current      │
 │ (the mic) │               │ Analyzer │              │   (queue)    │  readings     │ Screen       │
 └───────────┘               └──────────┘              └──────────────┘               └──────┬───────┘
 ◀─────────── AUDIO THREAD (runs non-stop) ───────────▶ ◀──────── MAIN / KIVY THREAD (30 fps) ──┼──────▶
                                                                                               │ (Milestone 4+)
                                                                                               ▼
                                                                         ┌──────────────────────────────┐
                                                                         │ game/  GameSession ─▶ Judge  │
                                                                         │        uses chart + instrument│
                                                                         └──────────────────────────────┘
```

In words:

1. **audio/** reads ~46 ms of microphone sound at a time (an `AudioBlock`).
2. **dsp/** (Digital Signal Processing) turns that block into numbers: loudness, pitch, note name (a `PitchReading`).
3. **ui/bridge.py** safely moves readings from the audio thread to the screen thread.
4. **ui/screens/** show the readings. The Tuner shows them directly.
5. *(Later)* the Play screen hands readings to **game/**, which compares them against the **chart** and produces scores.

---

## 2. The layers and their rules

| Folder | Job | May import | Must NOT import |
|---|---|---|---|
| `rsh/events.py` | The small data "messages" passed between layers | numpy | everything else |
| `rsh/dsp/` | Maths on audio: level, pitch, onsets, chords | numpy, `events`, `config` | kivy, jnius, android |
| `rsh/instruments/` | Facts about instruments (strings, chords) | `dsp/notes` | kivy, jnius, android |
| `rsh/game/` | Rules: charts, scoring, the song clock | `dsp`, `instruments`, `events` | kivy, jnius, android |
| `rsh/audio/` | Getting sound in (phone mic, laptop mic, fake) | numpy, jnius (Android file only) | kivy widgets |
| `rsh/platform/` | Android-only things like permissions | android | kivy widgets |
| `rsh/ui/` | Screens, widgets, `.kv` layouts | kivy and anything above | — |
| `rsh/app.py` | **Composition root**: creates every object and connects them | everything | — |

**The golden rule: dependencies point inward.** The UI knows about the game, and the game knows nothing about the UI. Why bother?

- **Testing:** `dsp/`, `instruments/` and `game/` run under plain `pytest` on a laptop in under a second. You can't easily unit-test code that needs a phone screen.
- **Swapping parts:** a better pitch detector, a different microphone API, or even moving to another UI framework touches one layer, not the whole app.
- **Finding things:** a pitch bug lives in `dsp/`, a drawing bug in `ui/`.

> A quick way to check yourself: if you type `import kivy` inside `dsp/` or `game/`, stop. That code belongs in `ui/`.

---

## 3. Threads (the most important concept in this app)

A **thread** is a line of work that runs at the same time as others. This app uses two:

| Thread | Who runs it | What it does | Rule |
|---|---|---|---|
| **Audio thread** | `AudioSource._run()` in `audio/source.py` | Waits for mic data, analyses it, pushes results | Must never wait for the UI, or audio gets dropped |
| **Main (Kivy) thread** | Kivy itself | Draws the screen, handles touches | **Only this thread may change widgets** |

They talk through **one** place: the queue in `ui/bridge.py`. The audio thread calls `bridge.push(reading)`, which never waits. A Kivy `Clock` timer on the main thread empties the queue 30 times per second.

Two other thread hops to know about:

- Android's permission answer arrives on *Android's* thread. `app.py` uses `@mainthread` to hop back.
- Never call `time.sleep()` on the main thread. The app will freeze.

---

## 4. Time: the audio clock

Every `AudioBlock` and `PitchReading` has a `time` computed from **how many samples have been recorded** (`start_sample / sample_rate`), not from the computer's clock. Samples arrive at an exactly steady rate, so this clock never jitters.

For the game (Milestones 4–6) this matters a lot:

```
song_time = audio_time - song_start_audio_time - latency_offset
```

- `latency_offset` is the delay between you plucking the string and the phone "hearing" it. It's about 40–80 ms on most phones, and the calibration screen (Milestone 6) measures it.
- With one steady clock and one offset, scoring is fair.

---

## 5. Design patterns used (and where)

| Pattern | Where | Why |
|---|---|---|
| **Template method** | `audio/source.py`: the base class owns the thread loop, and subclasses fill in `_open/_read_block/_close` | Each microphone backend is ~30 lines and can't get the threading wrong |
| **Factory** | `audio/factory.py` → `create_audio_source()` | The app never needs `if android:` checks |
| **Registry** | `instruments/registry.py` | Adding guitar = one new file + one `register()` line |
| **Dependency injection** | `Analyzer(pitch_function=...)`, `GameSession(chart, instrument, judge)` | Swap parts for tests or experiments without editing the class |
| **Immutable messages** | `@dataclass(frozen=True)` in `events.py` | Safe to pass between threads, because nothing can change them halfway |
| **Data-driven content** | `charts/*.json` | New songs don't need code changes |
| **Separate layout from logic** | `ui/kv/*.kv` (layout) vs `ui/screens/*.py` (behaviour) | Change how it looks without touching how it works |

---

## 6. How a feature should flow through the layers (example: scoring)

1. **Write the rule as a pure function or class** in `game/scoring.py`.
2. **Write tests first** in `tests/test_scoring.py` (they're already there and skipped).
3. **Use it from `game/session.py`**, still pure Python and still testable.
4. **Show it** in `ui/screens/play.py` and `ui/kv/screens.kv`.
5. **Connect it** in `app.py` only if a new object needs creating.

If you follow that order, every new feature is tested before it touches the UI.

---

## 7. Why Kivy, and what are the limits?

**Kivy works for this project.** Python + numpy is fast enough to analyse ukulele audio, and Android's `AudioRecord` (through `pyjnius`) gives raw microphone samples.

Things to know:

- **Latency:** expect ~40–80 ms between plucking and the app knowing. That's fine for scoring with ±60–140 ms windows plus calibration. It's *not* good enough to play your instrument's sound back through the phone (that needs <20 ms).
- **No scipy on Android.** Write DSP with numpy only. (An `aubio` recipe exists in python-for-android if you later want a fast C pitch/onset library.)
- **Kivy's last release** was 2.3.1 (Dec 2024). It's stable but moves slowly.
- **If it ever becomes too slow:** because `dsp/` and `game/` are pure Python, the *ideas* carry over to Godot 4 (GDScript, good for rhythm games) or native Kotlin + Oboe (lowest latency, much harder). Don't switch until you've measured a real problem on the phone.

---

## 8. Glossary

| Term | Meaning |
|---|---|
| **Sample** | One measurement of the microphone. 44,100 per second. |
| **Sample rate** | Samples per second (Hz). We use 44100. |
| **Block / buffer** | A chunk of samples processed together (2048 = 46 ms). |
| **FFT** | Fast Fourier Transform: splits a sound into the frequencies it contains. |
| **Fundamental** | The main frequency of a note (A4 = 440 Hz). |
| **Harmonics** | Extra frequencies at 2×, 3×, … the fundamental. They give an instrument its sound. |
| **Cents** | 1/100 of a semitone. ±5 cents sounds "in tune". |
| **MIDI number** | A whole number per note: C4 = 60, A4 = 69. |
| **Onset** | The instant a note starts (pluck/strum). |
| **Chroma** | 12 numbers saying how much of each note name (C … B) is in a sound. |
| **Latency** | Delay between something happening and the app reacting. |
| **Recipe** | python-for-android's build instructions for a package with C code (numpy, kivy). |
