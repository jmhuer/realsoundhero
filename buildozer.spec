# Buildozer turns this Python project into an Android app (.apk).
# Full list of options: https://buildozer.readthedocs.io/en/latest/specifications.html
# Build + install + run on a USB-connected phone:
#     buildozer android debug deploy run logcat

[app]
title = RealSoundHero
package.name = realsoundhero
package.domain = org.realsoundhero
version = 0.1.0

# Which files go into the app
source.dir = .
source.include_exts = py,kv,json,png,jpg,atlas,ttf,wav,ogg
source.exclude_dirs = tests, docs, bin, .venv, .buildozer, .git, .pytest_cache

# Python packages built *for the phone*. Each one needs a python-for-android
# "recipe" if it contains C code (numpy does, and so does kivy).
requirements = python3,kivy,numpy,pyjnius,android

orientation = portrait
fullscreen = 0

# --- Android ---------------------------------------------------------------
# RECORD_AUDIO = microphone. The app must *also* ask at runtime (rsh/platform/permissions.py).
android.permissions = RECORD_AUDIO

# Target the newest API Google Play requires, but still run on old phones (Android 7+).
android.api = 35
android.minapi = 24

# Modern phones (like the Pixel 9a) are 64-bit ARM. Building one arch is twice as fast.
android.archs = arm64-v8a

android.accept_sdk_license = True
android.allow_backup = True

# Pin python-for-android to one exact commit, so builds don't change under you.
# Why not the v2026.05.09 release? It fails installing pure-Python packages that
# have new Android wheels (e.g. charset-normalizer, which Kivy needs via requests).
# The develop branch fixes that (p4a PR #3366). Update the commit deliberately, now and then.
p4a.branch = develop
p4a.commit = d97d8071

[buildozer]
# 2 = show build commands (helpful when something breaks)
log_level = 2
warn_on_root = 1
