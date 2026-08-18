"""
Pinch (thumb-tip to index-tip) detection.

Distance between the two tips is normalized against the hand's own size
(wrist to middle-finger-base distance), so the pinch threshold stays
accurate regardless of how close or far the hand is from the camera.

Requires a minimum hold duration before counting as a real pinch (not a
single-frame flicker), and a maximum duration to count as a "tap"
(brief pinch-and-release, used for one-shot actions like a screenshot).
"""

import math
import time

THUMB_TIP = 4
INDEX_TIP = 8
WRIST = 0
MIDDLE_MCP = 9


class PinchDetector:
    def __init__(
        self,
        pinch_ratio_threshold: float = 0.25,
        min_tap_duration: float = 0.15,
        max_tap_duration: float = 0.6,
        cooldown_time: float = 1.0,
    ) -> None:
        self.pinch_ratio_threshold = pinch_ratio_threshold
        self.min_tap_duration = min_tap_duration
        self.max_tap_duration = max_tap_duration
        self.cooldown_time = cooldown_time

        self.pinch_start_time = None
        self.last_trigger_time = 0.0
        self.is_pinching = False

    def _distance(self, point_a, point_b) -> float:
        return math.hypot(point_a.x - point_b.x, point_a.y - point_b.y)

    def update(self, hand_landmarks, is_moving: bool = False) -> bool:
        """
        Feed the current hand's landmarks once per frame (None if no hand
        detected), and whether the hand is currently in translational
        motion (to ignore pinch readings during swipes). Returns True the
        moment a valid pinch-tap is confirmed.
        """
        now = time.time()

        if hand_landmarks is None or is_moving:
            self.pinch_start_time = None
            self.is_pinching = False
            return False

        hand_size = self._distance(hand_landmarks[WRIST], hand_landmarks[MIDDLE_MCP])
        if hand_size == 0:
            self.is_pinching = False
            return False

        pinch_distance = self._distance(hand_landmarks[THUMB_TIP], hand_landmarks[INDEX_TIP])
        ratio = pinch_distance / hand_size
        self.is_pinching = ratio < self.pinch_ratio_threshold

        if self.is_pinching:
            if self.pinch_start_time is None:
                self.pinch_start_time = now
            return False

        if self.pinch_start_time is not None:
            duration = now - self.pinch_start_time
            self.pinch_start_time = None
            is_valid_tap = self.min_tap_duration <= duration <= self.max_tap_duration
            is_past_cooldown = now - self.last_trigger_time >= self.cooldown_time
            if is_valid_tap and is_past_cooldown:
                self.last_trigger_time = now
                return True

        return False