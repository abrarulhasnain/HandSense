# HandSense

Control your laptop using hand gestures detected through your webcam — no cursor involved. Show a number with your fingers, and the mapped app opens. Swipe down to minimize. Make a fist to close.

> Status: **In active development.** This README reflects the target design and will be updated as features land.

---

## Overview

This project uses computer vision (not machine-learning classifiers, by design) to read hand landmarks in real time and translate specific hand poses into laptop actions — opening apps, minimizing windows, and closing them — without touching the mouse or keyboard.

The system is built to work across different webcams and lighting conditions, not tuned to one setup.

## Planned Features (V1)

| Gesture | Trigger | Action |
|---|---|---|
| Finger count 1–5 (one hand) | Hold steady for a moment | Opens the app mapped to that number |
| Finger count 6–10 (two hands combined) | Hold steady for a moment | Opens the app mapped to that number |
| Swipe down (open palm, downward motion) | Motion-based | Minimizes the active window |
| Fist (closed hand) | Hold steady for a moment | Closes the active window |

More gestures will be added as the gesture-action mapping system is generalized — the architecture is designed to make adding a new gesture a matter of configuration, not a rewrite.

## Why Rule-Based, Not ML

Hand pose recognition here is done through landmark geometry (finger-joint angles and relative positions) rather than a trained classifier. This keeps the system fast, explainable, and free of a training/dataset requirement — sufficient for well-defined static and motion-based poses. A learned classifier may be introduced later only if custom, user-trained gestures are added.

## Architecture

```
Webcam (OpenCV)
   → MediaPipe Hand Detection + Landmarks
   → Finger State Extraction (geometry rules)
   → Gesture Recognition (rule-based + state machine)
   → Gesture Validation (confidence threshold + dwell time + cooldown)
   → Action Dispatcher (OS-level app control)
   → Debug Overlay (FPS, current gesture, confidence)
```

Gesture recognition runs through a state machine to avoid false triggers from a single unstable frame:

```
IDLE → HAND_DETECTED → GESTURE_CANDIDATE → GESTURE_CONFIRMED → ACTION_EXECUTED → COOLDOWN → IDLE
```

## Project Structure

```
HandSense/
│
├── app/
│   ├── camera/       # Webcam capture and frame handling
│   ├── vision/        # MediaPipe hand detection and landmark extraction
│   ├── gestures/       # Gesture recognition rules and state machine
│   ├── controller/    # OS-level action dispatch (open/minimize/close apps)
│   ├── ui/            # Debug overlay / future GUI
│   ├── config/        # Gesture-to-action mappings, thresholds
│   └── utils/         # Shared helpers (logging, smoothing math, etc.)
│
├── tests/             # Vision, gesture, and system tests
├── models/            # MediaPipe model assets (if any are bundled)
├── assets/            # Screenshots, demo GIFs
├── logs/              # Runtime logs (not committed)
├── docs/              # Technical and learning documentation
├── requirements.txt
└── main.py
```

## Tech Stack

| Purpose | Library |
|---|---|
| Hand detection & landmarks | [MediaPipe](https://developers.google.com/mediapipe) |
| Frame capture & processing | [OpenCV](https://opencv.org/) |
| System/app control | [pynput](https://pynput.readthedocs.io/) |
| Numerical operations | [NumPy](https://numpy.org/) |

## Installation

```powershell
# Clone the repo, then from the project root:
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Running

```powershell
python main.py
```

*(Entry point and run instructions will be finalized as the app takes shape.)*

## Roadmap

- [ ] Webcam capture pipeline
- [ ] Hand detection + landmark overlay
- [ ] Finger-state extraction (geometry rules)
- [ ] Number-count gesture recognition (1–10, two hands)
- [ ] Swipe-down minimize gesture
- [ ] Fist close gesture
- [ ] Configurable gesture-to-app mapping
- [ ] Debug overlay (FPS, gesture, confidence)
- [ ] Additional custom gestures
- [ ] Packaging and polish

## Development Approach

Built incrementally, one milestone at a time, with real-device testing between each step rather than in one large push — see [`docs/`](./docs) for design notes as they're added.

## License

[MIT](./LICENSE)
