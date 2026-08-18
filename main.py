"""
Entry point for HandSense.

Phase 9: Adds pinch-tap for screenshots, alongside finger-count app
control, fist-close, and directional swipes. Press 'q' to quit.
"""

import math

import cv2

from app.camera.capture import Camera
from app.vision.hand_detector import HandDetector
from app.vision.finger_counter import count_fingers, get_palm_center
from app.gestures.state_machine import GestureStateMachine
from app.gestures.swipe_detector import SwipeDetector
from app.gestures.pinch_detector import PinchDetector
from app.controller.app_launcher import launch_app_for_gesture
from app.controller.window_controller import close_active_window, minimize_active_window
from app.controller.media_controller import send_previous, send_next, send_app_switch
from app.controller.screenshot_controller import take_screenshot

MOVEMENT_SUPPRESS_THRESHOLD = 0.02  # per-frame palm movement that counts as "actively moving"


def main() -> None:
    camera = Camera()
    detector = HandDetector()
    gesture_machine = GestureStateMachine(dwell_time=1.0, cooldown_time=1.0)
    swipe_detector = SwipeDetector()
    pinch_detector = PinchDetector()

    last_hand_pos = None

    print("HandSense - Phase 9: Pinch Screenshot")
    print("Press 'q' to quit.")

    while True:
        frame = camera.read_frame()
        if frame is None:
            print("Failed to read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame, result = detector.find_hands(frame)

        total_fingers = None
        hand_x = None
        hand_y = None
        first_hand_landmarks = None

        if result.hand_landmarks:
            total_fingers = sum(
                count_fingers(hand_landmarks) for hand_landmarks in result.hand_landmarks
            )
            first_hand_landmarks = result.hand_landmarks[0]
            hand_x, hand_y = get_palm_center(first_hand_landmarks)

        # Detect whether the hand is actively moving right now, so we can
        # avoid confirming a static number gesture mid-swipe.
        is_moving = False
        current_hand_pos = (hand_x, hand_y) if hand_x is not None else None
        if current_hand_pos and last_hand_pos:
            dx = current_hand_pos[0] - last_hand_pos[0]
            dy = current_hand_pos[1] - last_hand_pos[1]
            if math.hypot(dx, dy) > MOVEMENT_SUPPRESS_THRESHOLD:
                is_moving = True
        last_hand_pos = current_hand_pos

        if pinch_detector.update(first_hand_landmarks, is_moving):
            print("[INFO] Pinch tap detected.")
            take_screenshot()

        swipe_direction = swipe_detector.update(hand_x, hand_y)
        if swipe_direction == "down":
            print("[INFO] Swipe down detected.")
            minimize_active_window()
        elif swipe_direction == "up":
            print("[INFO] Swipe up detected.")
            send_app_switch()
        elif swipe_direction == "left":
            print("[INFO] Swipe left detected.")
            send_previous()
        elif swipe_direction == "right":
            print("[INFO] Swipe right detected.")
            send_next()

        # Suppress static number-gesture confirmation while the hand is
        # moving or pinching, so those states don't get misread as a hold.
        gesture_input = None if (is_moving or pinch_detector.is_pinching) else total_fingers
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