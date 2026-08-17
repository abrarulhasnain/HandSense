"""
Launches applications mapped to confirmed gestures, skipping the launch
if the target app is already running.
"""

import subprocess
import psutil

from app.config.gesture_mapping import GESTURE_APP_MAP


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
    Opens the app mapped to the given gesture number, unless it's already
    running - in which case the launch is silently skipped.
    """
    app_info = GESTURE_APP_MAP.get(gesture)
    if app_info is None:
        return  # no app mapped to this number

    if is_process_running(app_info["process_name"]):
        print(f"[INFO] {app_info['name']} is already running - skipping.")
        return

    try:
        subprocess.Popen(app_info["path"])
        print(f"[INFO] Launched {app_info['name']}.")
    except OSError as error:
        print(f"[ERROR] Failed to launch {app_info['name']}: {error}")
