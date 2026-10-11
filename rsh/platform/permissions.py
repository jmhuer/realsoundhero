"""Ask the user for microphone permission (Android only).

Android makes apps ask at runtime ("Allow RealSoundHero to record audio?").
Listing RECORD_AUDIO in buildozer.spec isn't enough. On desktop we just say
"yes".

Watch out: Android calls our callback on *its* thread, not Kivy's. The
caller has to hop back to the Kivy thread (app.py does this with
``@mainthread``).
"""
from typing import Callable

from rsh.platform import IS_ANDROID


def request_microphone_permission(on_result: Callable[[bool], None]) -> None:
    if not IS_ANDROID:
        on_result(True)
        return

    from android.permissions import Permission, check_permission, request_permissions

    if check_permission(Permission.RECORD_AUDIO):
        on_result(True)
        return

    def _callback(permissions, grants):
        on_result(all(grants))

    request_permissions([Permission.RECORD_AUDIO], _callback)
