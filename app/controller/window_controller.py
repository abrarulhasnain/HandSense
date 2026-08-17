"""
Controls the currently active (foreground) window - closing or minimizing
it via standard window messages, the same signals sent when clicking a
window's close/minimize buttons.
"""

import win32gui
import win32con

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
