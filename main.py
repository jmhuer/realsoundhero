"""Entry point.

Buildozer (and python-for-android) look for a file called ``main.py`` and run
it when the Android app starts. Keep this file tiny: all real code lives in
the ``rsh`` package so it can be organised and tested.

Run on your computer with:  python main.py
"""
from rsh.app import RealSoundHeroApp

if __name__ == "__main__":
    RealSoundHeroApp().run()
