"""
Swipe-down gesture detection.

Unlike static poses (fist, finger count), a swipe is motion over time,
so this tracks the wrist's vertical position across recent frames and
checks whether it moved downward by enough distance within a short
time window - while the hand is held open, to avoid confusing this
with an open-palm hand simply drifting down between other gestures.
"""

import time


class SwipeDetector:
    def __init__(
        self,
        time_window: float = 0.5,
        min_downward_distance: float = 0.25,
        cooldown_time: float = 1.5,
    ) -> None:
        self.time_window = time_window
        self.min_downward_distance = min_downward_distance
        self.cooldown_time = cooldown_time

        self.history = []  # list of (timestamp, wrist_y)
        self.last_trigger_time = 0.0

    def update(self, wrist_y, is_open_palm: bool) -> bool:
        """
        Feed the current wrist Y-position (0-1 range) and whether the hand
        is currently an open palm, once per frame. Returns True the moment
        a downward swipe is confirmed.
        """
        now = time.time()

        if not is_open_palm or wrist_y is None:
            self.history.clear()
            return False

        if now - self.last_trigger_time < self.cooldown_time:
            return False  # still in cooldown from the last swipe

        self.history.append((now, wrist_y))
        self.history = [(t, y) for t, y in self.history if now - t <= self.time_window]

        if len(self.history) < 2:
            return False

        oldest_y = self.history[0][1]
        newest_y = self.history[-1][1]
        downward_movement = newest_y - oldest_y  # y increases downward in image coordinates

        if downward_movement >= self.min_downward_distance:
            self.history.clear()
            self.last_trigger_time = now
            return True

        return False
