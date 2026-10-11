# Setup guide (start here if you're new)

These steps take you from a fresh computer to the app running on your Android phone. They were tested on **Ubuntu 22.04** with a **Pixel 9a**. Every command goes in a terminal. Lines starting with `#` are comments, so don't type them.

> **Words you'll see**
> - **Terminal:** the text window where you type commands.
> - **venv (virtual environment):** a private folder of Python packages just for this project, so it can't break other projects.
> - **APK:** an Android app file.
> - **adb:** "Android Debug Bridge", the tool that talks to your phone over USB.
> - **Buildozer:** the tool that packages Python + Kivy into an APK.

---

## Part A: Run the app on your computer (10 minutes)

### 1. Get the code
```bash
git clone https://github.com/jmhuer/realsoundhero.git
cd realsoundhero
```

### 2. System packages (one time)
```bash
sudo apt update
sudo apt install -y git zip unzip openjdk-17-jdk python3-pip python3-venv \
    autoconf automake libtool pkg-config zlib1g-dev libncurses5-dev \
    libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev build-essential \
    ccache libportaudio2
```
`libportaudio2` lets the desktop app use your laptop mic. Everything else is for building the Android app later.

### 3. Make a virtual environment and install Python packages
Use the **system** Python (`/usr/bin/python3`), *not* Anaconda/Miniconda. Conda is known to break Android builds.
```bash
/usr/bin/python3 -m venv .venv
source .venv/bin/activate          # do this every time you open a new terminal
pip install --upgrade pip
pip install -r requirements-dev.txt
```
Your prompt now starts with `(.venv)`. That means the venv is active.

> If `python3 -m venv` fails and you can't install `python3-venv`, use
> `/usr/bin/python3 -m pip install --user virtualenv && /usr/bin/python3 -m virtualenv .venv`.

### 4. Run the tests
```bash
pytest
```
You should see something like `27 passed, 5 skipped, 1 xfailed`.
- *skipped* = tests waiting for you to write the feature (Milestone 5).
- *xfailed* = a known weakness we expect to fail until Milestone 2.

### 5. Run the app
```bash
python main.py                    # uses your laptop microphone if it has one
RSH_FAKE_AUDIO=1 python main.py   # uses a fake ukulele that cycles G-C-E-A
```
Click **Tuner**. You should see notes and the level meter moving.

---

## Part B: Run the app on your Android phone

### 6. Prepare the phone (one time)
1. **Settings → About phone →** tap **Build number** 7 times. This turns on "Developer options".
2. **Settings → System → Developer options →** turn on **USB debugging**.
3. Plug the phone into the computer with USB. On the phone, tap **Allow** on the "Allow USB debugging?" popup.
4. Check the computer can see it:
   ```bash
   adb devices
   ```
   You should see a line ending in `device`. If it says `unauthorized`, look at the phone and accept the popup.
   (If `adb` isn't found: `sudo apt install adb`, or use the one from Android Studio in `~/Android/Sdk/platform-tools`.)

### 7. Use Java 17 for the build
Buildozer needs **JDK 17**. If you have several Java versions, point to 17 for this terminal:
```bash
export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
export PATH="$JAVA_HOME/bin:$PATH"
java -version        # should say 17
```
If you use conda, also take it off the PATH for this terminal: `conda deactivate` (repeat until `(base)` disappears), then `source .venv/bin/activate` again.

### 8. Build, install and run
```bash
buildozer -v android debug deploy run logcat
```
- `android debug` builds the APK into `bin/`.
- `deploy` installs it on the phone.
- `run` starts it.
- `logcat` shows the phone's log in your terminal. Press `Ctrl+C` to stop watching. The app keeps running.

**The first build takes 20–40 minutes.** It downloads the Android SDK/NDK (several GB, into `~/.buildozer`) and compiles Python, Kivy and numpy for ARM. Later builds take 1–3 minutes.

The phone will ask **"Allow RealSoundHero to record audio?"**. Tap **While using the app**. Then open **Tuner** and pluck a string.

### 9. Handy commands
```bash
buildozer android debug deploy run   # rebuild + install + start (after code changes)
adb logcat -s python                 # only show Python's messages (print(), errors)
adb install -r bin/*.apk             # reinstall the last APK without rebuilding
adb uninstall org.realsoundhero.realsoundhero
adb exec-out screencap -p > screen.png   # screenshot of the phone
```

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `Aidl not found` or SDK license errors | `rm -rf ~/.buildozer` and build again. `android.accept_sdk_license = True` is already set in buildozer.spec. |
| Build fails compiling something with "Cython" in the error | `pip install "cython<3"` in the venv, then `buildozer android clean` and rebuild |
| `... .whl is not a supported wheel on this platform` | A python-for-android bug with packages that ship Android wheels. Fixed on p4a `develop`, which is why buildozer.spec pins `p4a.commit`. If you change the pin, run `buildozer android clean`. |
| `cannot import name ... from 'pip._internal...'` | A half-upgraded build venv. Delete `.buildozer/android/platform/build-arm64-v8a` and build again. |
| Weird errors after changing `requirements` in buildozer.spec | `buildozer android clean` (rebuilds everything, slow) |
| App opens then closes immediately | Run `adb logcat -s python` and look for a `Traceback`. Usually a Python error or a missing file extension in `source.include_exts`. |
| Tuner shows nothing on the phone | Check the permission: Settings → Apps → RealSoundHero → Permissions → Microphone |
| `adb devices` shows nothing | Try another USB cable or port, set USB mode to "File transfer", then re-accept the debugging popup |
| `Unsupported class file major version` | Wrong Java. Repeat step 7. |

---

## Versions this was tested with
See the table in the README ("Tested toolchain").
