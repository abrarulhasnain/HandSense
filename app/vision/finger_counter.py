"""
Finger state detection using landmark geometry.

Uses distance-based comparisons rather than simple up/down position,
so detection stays accurate regardless of hand rotation or tilt.
The thumb uses a different reference point than the other four fingers
because it folds *across* the palm rather than curling toward the wrist.
"""

import math

FINGER_TIPS = [8, 12, 16, 20]         # index, middle, ring, pinky
FINGER_BASE_JOINTS = [6, 10, 14, 18]   # reference joint for each of the above

THUMB_TIP = 4
THUMB_IP = 3          # joint just below the thumb tip
PINKY_MCP = 17         # used as thumb's reference point instead of the wrist

WRIST = 0


def _distance(point_a, point_b) -> float:
    return math.hypot(point_a.x - point_b.x, point_a.y - point_b.y)


def get_finger_states(hand_landmarks) -> list[int]:
    """
    Returns a list of 5 values (0 or 1) for [thumb, index, middle, ring, pinky],
    where 1 means the finger is extended (open) and 0 means folded (closed).
    """
    states = []

    # --- Thumb: compare distance to the pinky's base joint, not the wrist ---
    # A folded thumb crosses toward the pinky side of the palm; an extended
    # thumb moves away from it. This holds regardless of hand rotation.
    pinky_mcp = hand_landmarks[PINKY_MCP]
    thumb_tip_distance = _distance(hand_landmarks[THUMB_TIP], pinky_mcp)
    thumb_ip_distance = _distance(hand_landmarks[THUMB_IP], pinky_mcp)
    states.append(1 if thumb_tip_distance > thumb_ip_distance else 0)

    # --- Other 4 fingers: tip farther from wrist than its base = extended ---
    wrist = hand_landmarks[WRIST]
    for tip_idx, base_idx in zip(FINGER_TIPS, FINGER_BASE_JOINTS):
        tip_distance = _distance(hand_landmarks[tip_idx], wrist)
        base_distance = _distance(hand_landmarks[base_idx], wrist)
        states.append(1 if tip_distance > base_distance else 0)

    return states


def count_fingers(hand_landmarks) -> int:
    """Returns how many fingers are extended (0-5) for a single hand."""
    return sum(get_finger_states(hand_landmarks))
