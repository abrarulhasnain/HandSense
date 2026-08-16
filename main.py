"""
Entry point for HandSense.

Phase 1: Opens the webcam and overlays detected hand landmarks in real time.
Press 'q' to quit.
"""

import cv2

from app.camera.capture import Camera
from app.vision.hand_detector import HandDetector


def main() -> None:
    camera = Camera()
    detector = HandDetector()

    print("HandSense - Phase 1: Hand Detection")
    print("Press 'q' to quit.")

    while True:
        frame = camera.read_frame()
        if frame is None:
            print("Failed to read frame from webcam.")
            break

        frame = cv2.flip(frame, 1)  # Mirror view feels more natural
        frame, results = detector.find_hands(frame)

        cv2.imshow("HandSense", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    camera.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
