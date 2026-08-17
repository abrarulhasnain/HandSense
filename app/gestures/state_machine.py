"""
Gesture stability state machine.

Prevents accidental triggers by requiring a gesture to stay stable for
a minimum "dwell time" before it counts as confirmed. Once confirmed, the
same gesture will not fire again until the hand changes to something else
(a different gesture, or no hand at all) - holding it steady won't
repeatedly re-trigger the action.
"""

import time


class GestureStateMachine:
    STATE_IDLE = "IDLE"
    STATE_CANDIDATE = "CANDIDATE"
    STATE_HELD = "HELD"

    def __init__(self, dwell_time: float = 1.0, cooldown_time: float = 1.0) -> None:
        self.dwell_time = dwell_time
        self.cooldown_time = cooldown_time  # minimum gap between two DIFFERENT confirmed gestures

        self.state = self.STATE_IDLE
        self.candidate_gesture = None
        self.candidate_start_time = None
        self.last_confirmed_gesture = None
        self.last_confirm_time = 0.0

    def update(self, current_gesture):
        """
        Feed the latest detected gesture (e.g. an integer finger count) in
        every frame. Returns the confirmed gesture the moment it's accepted,
        or None if nothing should trigger yet.
        """
        now = time.time()

        # Hand removed, or gesture changed away from what's currently held
        if current_gesture is None:
            self.state = self.STATE_IDLE
            self.candidate_gesture = None
            self.last_confirmed_gesture = None
            return None

        if self.state == self.STATE_HELD:
            if current_gesture != self.last_confirmed_gesture:
                # Gesture changed while a previous one was held - start fresh
                self.state = self.STATE_CANDIDATE
                self.candidate_gesture = current_gesture
                self.candidate_start_time = now
                self.last_confirmed_gesture = None
            return None  # still holding the same confirmed gesture - no re-trigger

        if self.state == self.STATE_IDLE:
            self.state = self.STATE_CANDIDATE
            self.candidate_gesture = current_gesture
            self.candidate_start_time = now
            return None

        if self.state == self.STATE_CANDIDATE:
            if current_gesture != self.candidate_gesture:
                # Gesture changed before it stabilized - restart the timer
                self.candidate_gesture = current_gesture
                self.candidate_start_time = now
                return None

            if now - self.candidate_start_time >= self.dwell_time:
                if now - self.last_confirm_time < self.cooldown_time:
                    return None  # too soon after the previous different gesture
                confirmed = self.candidate_gesture
                self.state = self.STATE_HELD
                self.last_confirmed_gesture = confirmed
                self.last_confirm_time = now
                return confirmed

            return None

    def get_status(self) -> str:
        """Returns a human-readable status string, useful for the debug overlay."""
        if self.state == self.STATE_CANDIDATE:
            import time as _time
            elapsed = _time.time() - self.candidate_start_time
            remaining = max(0.0, self.dwell_time - elapsed)
            return f"HOLDING ({remaining:.1f}s)"
        if self.state == self.STATE_HELD:
            return f"CONFIRMED: {self.last_confirmed_gesture} (release to reset)"
        return "IDLE"
