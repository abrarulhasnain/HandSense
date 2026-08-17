"""
Entry point for HandSense.

Phase 8 (fixed): Suppresses static gesture confirmation while the hand is
actively moving, so an open palm mid-swipe doesn't also get read as the
"5" finger-count gesture. Press 'q' to quit.
"""

import math

import cv2

from app.camera.capture import Camera
from app.vision.hand_detector import HandDetector
from app.vision.finger_counter import count_fingers
from app.gestures.state_machine import GestureStateMachine
from app.gestures.swipe_detector import SwipeDetector
from app.controller.app_launcher import launch_app_for_gesture
from app.controller.window_controller import close_active_window, minimize_active_window
from app.controller.media_controller import send_previous, send_next

WRIST = 0
MOVEMENT_SUPPRESS_THRESHOLD = 0.02  # per-frame wrist movement that counts as "actively moving"


def main() -> None:
    camera = Camera()
    detector = HandDetector()
    gesture_machine = GestureStateMachine(dwell_time=1.0, cooldown_time=1.0)
    swipe_detector = SwipeDetector()

    last_wrist_pos = None

    print("HandSense - Phase 8: Directional Swipe")
    print("Press 'q' to quit.")

    while True:
        frame = camera.read_frame()
        if frame is None:
            print("Failed to read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame, result = detector.find_hands(frame)

        total_fingers = None
        wrist_x = None
        wrist_y = None
        is_open_palm = False

        if result.hand_landmarks:
            total_fingers = sum(
                count_fingers(hand_landmarks) for hand_landmarks in result.hand_landmarks
            )
            wrist_x = result.hand_landmarks[0][WRIST].x
            wrist_y = result.hand_landmarks[0][WRIST].y
            is_open_palm = total_fingers >= 4

        # Detect whether the hand is actively moving right now, so we can
        # avoid confirming a static number gesture mid-swipe.
        is_moving = False
        current_wrist_pos = (wrist_x, wrist_y) if wrist_x is not None else None
        if current_wrist_pos and last_wrist_pos:
            dx = current_wrist_pos[0] - last_wrist_pos[0]
            dy = current_wrist_pos[1] - last_wrist_pos[1]
            if math.hypot(dx, dy) > MOVEMENT_SUPPRESS_THRESHOLD:
                is_moving = True
        last_wrist_pos = current_wrist_pos

        swipe_direction = swipe_detector.update(wrist_x, wrist_y, is_open_palm)
        if swipe_direction == "down":
            print("[INFO] Swipe down detected.")
            minimize_active_window()
        elif swipe_direction == "left":
            print("[INFO] Swipe left detected.")
            send_previous()
        elif swipe_direction == "right":
            print("[INFO] Swipe right detected.")
            send_next()

        # Only feed the finger count to the stability state machine when the
        # hand isn't actively moving - prevents a mid-swipe open palm from
        # also being read as a held "5" gesture.
        gesture_input = None if is_moving else total_fingers
        confirmed_gesture = gesture_machine.update(gesture_input)
        if confirmed_gesture is not None:
            print(f"[INFO] Gesture confirmed: {confirmed_gesture}")
            if confirmed_gesture == 0:
                close_active_window()
            else:
                launch_app_for_gesture(confirmed_gesture)

        display_count = total_fingers if total_fingers is not None else "-"
        cv2.putText(
            frame, f"Fingers: {display_count}", (30, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3,
        )
        cv2.putText(
            frame, gesture_machine.get_status(), (30, 110),
            cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 200, 255), 2,
        )

        cv2.imshow("HandSense", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()