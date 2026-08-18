"""
Launches applications mapped to confirmed gestures. If the app is already
running, its window is restored and brought to the foreground instead of
opening a duplicate - so showing the same gesture again pops a minimized
app back into view.
"""

import os
import psutil

from app.config.gesture_mapping import GESTURE_APP_MAP
from app.controller.window_controller import find_window_by_process_name, restore_and_focus_window


def is_process_running(process_name: str) -> bool:
    """Checks whether a process with the given name is currently running."""
    for process in psutil.process_iter(["name"]):
        try:
            if process.info["name"] and process.info["name"].lower() == process_name.lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def launch_app_for_gesture(gesture: int) -> None:
    """
    Opens the app mapped to the given gesture number. If it's already
    running, its window is restored/focused instead of launching a
    duplicate (except for apps marked always_launch, like File Explorer,
    where a new window is the expected behavior).
    """
    app_info = GESTURE_APP_MAP.get(gesture)
    if app_info is None:
        return  # no app mapped to this number

    if not app_info.get("always_launch", False):
        if is_process_running(app_info["process_name"]):
            hwnd = find_window_by_process_name(app_info["process_name"])
            if hwnd:
                restore_and_focus_window(hwnd)
                print(f"[INFO] {app_info['name']} restored to foreground.")
            else:
                print(f"[INFO] {app_info['name']} is already running - skipping.")
            return

    resolved_path = os.path.expandvars(app_info["path"])

    try:
        os.startfile(resolved_path)
        print(f"[INFO] Launched {app_info['name']}.")
    except OSError as error:
        print(f"[ERROR] Failed to launch {app_info['name']}: {error}")