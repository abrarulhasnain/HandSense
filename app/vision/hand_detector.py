"""
Hand detection and landmark drawing using the MediaPipe Tasks API.
"""

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 21-landmark connections, drawn manually since the legacy `solutions`
# module (which used to provide this) no longer exists in mediapipe 1.x
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),          # Index
    (5, 9), (9, 10), (10, 11), (11, 12),     # Middle
    (9, 13), (13, 14), (14, 15), (15, 16),   # Ring
    (13, 17), (17, 18), (18, 19), (19, 20),  # Pinky
    (0, 17),                                  # Palm base
]


class HandDetector:
    def __init__(
        self,
        model_path: str = "models/hand_landmarker.task",
        max_hands: int = 2,
        min_detection_confidence: float = 0.7,
        min_tracking_confidence: float = 0.7,
    ) -> None:
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_hands=max_hands,
            min_hand_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence,
        )
        self.detector = vision.HandLandmarker.create_from_options(options)
        self.frame_timestamp_ms = 0

    def find_hands(self, frame, draw: bool = True):
        """
        Detects hands in the given BGR frame.

        Returns the (possibly annotated) frame and the raw detection result,
        so gesture logic can use landmark coordinates later.
        """
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        self.frame_timestamp_ms += 33  # approx. one frame at ~30 FPS
        result = self.detector.detect_for_video(mp_image, self.frame_timestamp_ms)

        if draw and result.hand_landmarks:
            height, width, _ = frame.shape
            for hand_landmarks in result.hand_landmarks:
                points = [(int(lm.x * width), int(lm.y * height)) for lm in hand_landmarks]

                for start_idx, end_idx in HAND_CONNECTIONS:
                    cv2.line(frame, points[start_idx], points[end_idx], (0, 255, 0), 2)

                for point in points:
                    cv2.circle(frame, point, 4, (0, 0, 255), -1)

        return frame, result
