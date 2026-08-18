"""
Takes a full-screen screenshot and saves it to a timestamped file in the
user's Pictures folder, with a brief white flash overlay as visual
confirmation that the screenshot was captured.
"""

import os
import time
import tkinter as tk

from PIL import ImageGrab

SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), "Pictures", "HandSense_Screenshots")


def _show_flash() -> None:
    """Briefly shows a full-screen white overlay, like a camera flash."""
    flash_window = tk.Tk()
    flash_window.attributes("-fullscreen", True)
    flash_window.attributes("-alpha", 0.7)
    flash_window.attributes("-topmost", True)
    flash_window.configure(background="white")
    flash_window.update()
    flash_window.after(150, flash_window.destroy)
    flash_window.mainloop()


def take_screenshot() -> None:
    """Captures the full screen, saves it as a PNG, and flashes the screen."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)
    filename = f"handsense_{time.strftime('%Y%m%d_%H%M%S')}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    image = ImageGrab.grab()
    image.save(filepath)
    print(f"[INFO] Screenshot saved: {filepath}")

    _show_flash()