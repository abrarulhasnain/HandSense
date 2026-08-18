"""
Directional swipe detection (down / left / right).

Tracks the hand's palm-center position over a short rolling time window
and reports whichever direction moved the most, as long as it crosses a
minimum distance threshold - so a mostly-vertical movement with a little
sideways drift still reads as "down", not as a diagonal false trigger.

Unlike static gestures (finger count, fist), this doesn't require a
specific finger count - motion itself is the signal, since finger counts
can fluctuate briefly during fast hand movement due to camera perspective.
"""

import time


class SwipeDetector:
    def __init__(
        self,
        time_window: float = 0.5,
        min_distance: float = 0.20,
        cooldown_time: float = 1.0,
    ) -> None:
        self.time_window = time_window
        self.min_distance = min_distance
        self.cooldown_time = cooldown_time

        self.history = []  # list of (timestamp, x, y)
        self.last_trigger_time = 0.0

    def update(self, hand_x, hand_y):
        """
        Feed the current palm-center (x, y) position (0-1 range) once per
        frame, or (None, None) if no hand is detected. Returns "down",
        "left", "right", or None.
        """
        now = time.time()

        if hand_x is None or hand_y is None:
            self.history.clear()
            return None

        if now - self.last_trigger_time < self.cooldown_time:
            return None

        self.history.append((now, hand_x, hand_y))
        self.history = [(t, x, y) for t, x, y in self.history if now - t <= self.time_window]

        if len(self.history) < 2:
            return None

        _, oldest_x, oldest_y = self.history[0]
        _, newest_x, newest_y = self.history[-1]
        dx = newest_x - oldest_x
        dy = newest_y - oldest_y

        direction = None
        if abs(dy) >= self.min_distance and abs(dy) >= abs(dx):
            if dy > 0:
                direction = "down"
        elif abs(dx) >= self.min_distance and abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"

        if direction is not None:
            self.history.clear()
            self.last_trigger_time = now

        return direction