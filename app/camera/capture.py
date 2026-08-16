"""
Webcam capture wrapper.

Handles opening the camera, reading frames, and releasing resources.
"""

import cv2


class Camera:
    def __init__(self, camera_index: int = 0, width: int = 1280, height: int = 720) -> None:
        self.capture = cv2.VideoCapture(camera_index)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

        if not self.capture.isOpened():
            raise RuntimeError("Could not open webcam. Check camera index or permissions.")

    def read_frame(self):
        """Reads a single frame from the webcam. Returns None if the read fails."""
        success, frame = self.capture.read()
        if not success:
            return None
        return frame

    def release(self) -> None:
        """Releases the webcam resource."""
        self.capture.release()
