"""Helpers for things that differ between Android and desktop."""
import os

# python-for-android sets this environment variable when the app runs on a phone.
IS_ANDROID = "ANDROID_ARGUMENT" in os.environ
