"""
Entry point for HandSense.

Phase 7: Adds swipe-down detection (open palm moving down) to minimize
the active window, alongside finger-count app-launch and fist-close.
Press 'q' to quit.
"""

import cv2

from app.camera.capture import Camera
from app.vision.hand_detector import HandDetector
from app.vision.finger_counter import count_fingers
from app.gestures.state_machine import GestureStateMachine
from app.gestures.swipe_detector import SwipeDetector
from app.controller.app_launcher import launch_app_for_gesture
from app.controller.window_controller import close_active_window, minimize_active_window

WRIST = 0


def main() -> None:
    camera = Camera()
    detector = HandDetector()
    gesture_machine = GestureStateMachine(dwell_time=1.0, cooldown_time=1.0)
    swipe_detector = SwipeDetector()

    print("HandSense - Phase 7: Swipe to Minimize")
    print("Press 'q' to quit.")

    while True:
        frame = camera.read_frame()
        if frame is None:
            print("Failed to read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)
        frame, result = detector.find_hands(frame)

        total_fingers = None
        wrist_y = None
        is_open_palm = False

        if result.hand_landmarks:
            total_fingers = sum(
                count_fingers(hand_landmarks) for hand_landmarks in result.hand_landmarks
            )
            # Use the first detected hand's wrist for swipe tracking
            wrist_y = result.hand_landmarks[0][WRIST].y
            is_open_palm = total_fingers >= 4

        if swipe_detector.update(wrist_y, is_open_palm):
            print("[INFO] Swipe down detected.")
            minimize_active_window()

        confirmed_gesture = gesture_machine.update(total_fingers)
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
