"""
Sends keyboard key presses for actions like page/list navigation - used
for things standard system APIs can't directly control (a PDF reader's
current page, a webpage's focused element like a Netflix row).
"""

from pynput.keyboard import Controller, Key

keyboard = Controller()


def send_previous() -> None:
    """Sends the Left Arrow key - previous page / scroll list left."""
    keyboard.press(Key.left)
    keyboard.release(Key.left)
    print("[INFO] Sent Left Arrow (previous).")


def send_next() -> None:
    """Sends the Right Arrow key - next page / scroll list right."""
    keyboard.press(Key.right)
    keyboard.release(Key.right)
    print("[INFO] Sent Right Arrow (next).")
