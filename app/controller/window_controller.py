"""
Controls windows - closing, minimizing, or restoring them via standard
window messages and Win32 APIs.
"""

import win32gui
import win32con
import win32process
import psutil

# Never act on our own app's window, even if it happens to be focused
PROTECTED_WINDOW_TITLES = ["HandSense"]


def _get_safe_foreground_window():
    """Returns (hwnd, title) for the active window, or (None, None) if unsafe/unavailable."""
    hwnd = win32gui.GetForegroundWindow()

    if hwnd == 0:
        print("[INFO] No active window found.")
        return None, None

    title = win32gui.GetWindowText(hwnd)

    if not title:
        print("[INFO] Active window has no title - skipping for safety.")
        return None, None

    if any(protected.lower() in title.lower() for protected in PROTECTED_WINDOW_TITLES):
        print(f"[INFO] Skipping - '{title}' is a protected window.")
        return None, None

    return hwnd, title


def close_active_window() -> None:
    """Closes the currently focused window, unless it's a protected one."""
    hwnd, title = _get_safe_foreground_window()
    if hwnd is None:
        return
    win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    print(f"[INFO] Closed active window: {title}")


def minimize_active_window() -> None:
    """Minimizes the currently focused window, unless it's a protected one."""
    hwnd, title = _get_safe_foreground_window()
    if hwnd is None:
        return
    win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    print(f"[INFO] Minimized active window: {title}")


def find_window_by_process_name(process_name: str):
    """
    Finds a visible top-level window belonging to a process with the given
    name. Returns the window handle, or None if no such window is found
    (e.g. the process is running in the background with no visible window).
    """
    target_pids = {
        process.info["pid"]
        for process in psutil.process_iter(["pid", "name"])
        if process.info["name"] and process.info["name"].lower() == process_name.lower()
    }
    if not target_pids:
        return None

    matching_windows = []

    def _collect(hwnd, _):
        if not win32gui.IsWindowVisible(hwnd) or not win32gui.GetWindowText(hwnd):
            return True
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        if pid in target_pids:
            matching_windows.append(hwnd)
        return True

    win32gui.EnumWindows(_collect, None)
    return matching_windows[0] if matching_windows else None


def restore_and_focus_window(hwnd) -> None:
    """Restores a minimized window and brings it to the foreground."""
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    win32gui.SetForegroundWindow(hwnd)