# Learning path

A suggested order for growing this app, with the concepts each step teaches. Each milestone matches the TODO list in the [README](../README.md#todo-roadmap).

The habit to build: **make one small change → run `pytest` → run the app on the desktop → (sometimes) on the phone → commit.**

---

### Milestone 1: Get comfortable (done in the skeleton)
- **Do:** Read `main.py` → `rsh/app.py` → `rsh/ui/screens/tuner.py` → `rsh/dsp/analyzer.py`. Change a colour in `screens.kv` and see it change.
- **Learn:** Kivy `App`, `ScreenManager`, `.kv` files, properties (`StringProperty`) and how they auto-update the screen.
- **Read:** [Kivy Getting Started](https://kivy.org/doc/stable/gettingstarted/intro.html), [Kv language](https://kivy.org/doc/stable/guide/lang.html)

### Milestone 2: A tuner you can trust
- **Do:** Implement `detect_pitch_yin()` in `rsh/dsp/pitch.py`. Make `test_strong_second_harmonic` pass by removing its `xfail`. Add smoothing in `Analyzer`.
- **Learn:** numpy arrays and vectorisation (no Python `for` loops over samples!), autocorrelation, what harmonics are.
- **Read:** YIN paper (de Cheveigné & Kawahara, 2002). Search "YIN pitch detection numpy" for examples.
- **Try:** record a real uke on your laptop (`sounddevice`) and save blocks with `np.save`. Turn them into test cases.

### Milestone 3: Hearing *when* you play
- **Do:** Implement `OnsetDetector` in `rsh/dsp/onset.py` (spectral flux). Add an `Onset` event to `events.py`. Show a flash on the Tuner when an onset fires.
- **Learn:** spectra over time, thresholds, why a "refractory period" stops double-triggers.

### Milestone 4: The note highway
- **Do:** In `GameSession`, implement `start`, `song_time` and `upcoming`. In `PlayScreen`, draw falling notes with `kivy.graphics` on a `Clock.schedule_interval`.
- **Learn:** Kivy canvas instructions, game loops, mapping time → pixels (`y = hit_line + (note.time - now) * speed`).

### Milestone 5: Scoring
- **Do:** Remove `skip` in `tests/test_scoring.py` and implement `Judge.judge()`. Then `GameSession.handle_readings()`. Show score, combo, and "Perfect/Good/Miss".
- **Learn:** test-driven development, matching two event lists by time.

### Milestone 6: Latency calibration
- **Do:** A screen that plays a click every beat (Kivy `SoundLoader`). The player plucks along, you average `(pluck_time - click_time)`, and you save it as `latency_offset`.
- **Learn:** why every rhythm game has this screen, and saving settings with `kivy.storage.jsonstore.JsonStore`.

### Milestone 7: Chords
- **Do:** Implement `chroma_vector()` and `chord_match()` in `rsh/dsp/chroma.py`. Let charts use `"chord": "C"`.
- **Learn:** pitch classes and cosine similarity. Also *why the game knowing the expected chord makes detection much easier*.

### Milestone 8: Real app polish
- **Do:** Song select screen (list `charts/*.json`), results screen, high scores (JsonStore), an app icon (`icon.filename` in buildozer.spec).

### Milestone 9: Second instrument
- **Do:** `rsh/instruments/guitar.py` + `register()`. If you had to edit dsp/ or game/ to make it work, that's a sign some ukulele assumption leaked in. Fix it there.
- **Learn:** this is the payoff of modular design.

### Milestone 10: Performance
- **Do:** Log how long `Analyzer.process` takes on the phone (`time.perf_counter()`). It must stay well under the block duration (46 ms). If not, try the `aubio` recipe or smaller FFTs.

### Milestone 11+: Stretch goals
- Backing track playback in sync with the chart.
- Chart editor or importer (e.g. from MIDI files).
- GitHub Actions to build the APK automatically.

---

## General tips
- **Use `git` often.** Commit when something works, so you can always go back.
- **Read the logs.** On the phone: `adb logcat -s python`. Python errors appear there.
- **Desktop first.** Every phone build takes minutes, while desktop runs take seconds. Only build for the phone when you need the real mic or want to check speed.
- **Small steps.** If something breaks, you'll know it was the last small thing you changed.
