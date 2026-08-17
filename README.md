# HandSense

Control your laptop using hand gestures detected through your webcam — no cursor, no touch. Show a number with your fingers to open an app, swipe down to minimize a window, or make a fist to close it.

## Overview

HandSense reads hand landmarks in real time using MediaPipe and translates specific hand poses and motions into OS-level actions. Gesture recognition is entirely **rule-based geometry** — no trained classifier, no dataset — which keeps it fast, explainable, and easy to extend.

Every gesture goes through a stability check before it fires: a pose has to hold steady for about a second before it's accepted, and each confirmed gesture only fires once until the hand changes, so nothing gets accidentally triggered or repeated by holding a pose.

## Features (Working)

| Gesture | Trigger | Action |
|---|---|---|
| Finger count 1–3 *(extendable to 10 across two hands)* | Hold steady ~1s | Opens the mapped app — skips launch if it's already running |
| Fist (0 fingers) | Hold steady ~1s | Closes the active window (protects HandSense's own window) |
| Open palm, swipe down | Downward motion while open | Minimizes the active window |

App mappings are defined in `app/config/gesture_mapping.py` and are meant to be edited — no code changes needed to remap a gesture to a different app.

## Why Rule-Based, Not ML

Finger states and swipes are computed from landmark geometry (distances and relative positions between the 21 hand landmarks MediaPipe provides), not a trained classifier. This avoids needing a dataset or training step, keeps latency low, and makes every decision traceable back to a simple rule. A learned classifier may be introduced later only if user-trainable custom gestures are added.

## Architecture

Webcam (OpenCV)
→ MediaPipe HandLandmarker (21 landmarks per hand)
→ Finger State Extraction (distance-based geometry rules)
→ Gesture Recognition
├── Static gestures (finger count / fist) → Stability State Machine
└── Motion gesture (swipe) → Rolling position history
→ Action Dispatch (app launch / window close / window minimize)
→ Debug Overlay (finger count, gesture status)


**Stability state machine** (for static gestures — finger counts, fist):

IDLE → CANDIDATE (dwell timer running) → HELD (confirmed, won't re-fire) → IDLE (on release/change)


**Swipe detection** (motion-based, no dwell needed — tracks wrist Y-position over a short rolling time window and checks for consistent downward movement while the hand is open).

See [`docs/architecture.md`](./docs/architecture.md) for the full breakdown and [`docs/gestures.md`](./docs/gestures.md) for gesture-by-gesture detection details.

## Project Structure

HandSense/
│
├── app/
│ ├── camera/ # Webcam capture (app/camera/capture.py)
│ ├── vision/ # Hand detection + finger-state geometry
│ ├── gestures/ # Stability state machine + swipe detector
│ ├── controller/ # App launching, window close/minimize
│ ├── ui/ # Reserved for future GUI
│ ├── config/ # Gesture → app mapping
│ └── utils/ # Reserved for shared helpers
│
├── tests/ # Reserved for automated tests
├── models/ # hand_landmarker.task (downloaded, not committed)
├── docs/ # Architecture and gesture documentation
├── main.py # Entry point
└── requirements.txt


## Tech Stack

| Purpose | Library |
|---|---|
| Hand detection & landmarks | [MediaPipe](https://developers.google.com/mediapipe) (Tasks API — `HandLandmarker`) |
| Frame capture & processing | [OpenCV](https://opencv.org/) |
| App launching / process check | `subprocess`, [psutil](https://github.com/giampaolo/psutil) |
| Window close/minimize | [pywin32](https://github.com/mhammond/pywin32) |
| Numerical operations | [NumPy](https://numpy.org/) |

## Installation

```powershell
git clone <your-repo-url>
cd HandSense

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Download the hand landmark model (not committed to the repo — see `.gitignore`):

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "models\hand_landmarker.task"
```

## Running

```powershell
python main.py
```

A window opens showing the webcam feed with hand landmarks overlaid, current finger count, and gesture status. Press `q` to quit.

## Configuring App Mappings

Edit `app/config/gesture_mapping.py`:

```python
GESTURE_APP_MAP = {
    1: {"name": "Notepad", "path": "notepad.exe", "process_name": "notepad.exe"},
    # add entries for gestures 2-10 here
}
```

`process_name` is used to detect whether the app is already running, so a repeated gesture doesn't open duplicate windows.

## Roadmap

- [x] Webcam capture pipeline
- [x] Hand detection + landmark overlay
- [x] Finger-state extraction (rotation-independent geometry)
- [x] Number-count gesture recognition (currently 1–3 mapped, extendable to 10)
- [x] Gesture stability (dwell time, no repeat-fire while held)
- [x] App launch with duplicate prevention
- [x] Fist → close active window (with self-protection)
- [x] Swipe down → minimize active window
- [ ] Full 1–10 app mapping
- [ ] On-screen FPS + confidence overlay
- [ ] Additional custom gestures
- [ ] GUI for configuration/calibration
- [ ] Packaging and polish

## Safety

- The system never targets its own window for close/minimize actions.
- No destructive file/system operations are performed — only launching apps and standard window close/minimize signals (the same ones sent by clicking a window's own buttons).
- Every action requires the triggering gesture to hold steady for a minimum duration before firing, to avoid accidental triggers from momentary hand movement.

## License

[MIT](./LICENSE)
'@ | Set-Content -Encoding UTF8 README.md
2. Technical docs banao
powershell
@'
# Architecture

## Pipeline

Webcam (OpenCV)
→ MediaPipe HandLandmarker (21 landmarks per hand, Tasks API)
→ Finger State Extraction (app/vision/finger_counter.py)
→ Gesture Recognition
├── Static: finger count / fist → Stability State Machine (app/gestures/state_machine.py)
└── Motion: swipe down → Rolling position history (app/gestures/swipe_detector.py)
→ Action Dispatch
├── app/controller/app_launcher.py → opens mapped apps, skips if already running
└── app/controller/window_controller.py → close / minimize active window
→ Debug Overlay (cv2 text on the live frame)


## Module Responsibilities

| Module | Responsibility |
|---|---|
| `app/camera/capture.py` | Opens the webcam, reads frames, releases the resource cleanly |
| `app/vision/hand_detector.py` | Runs MediaPipe's `HandLandmarker`, draws landmarks on the frame |
| `app/vision/finger_counter.py` | Converts raw landmark coordinates into a 5-element open/closed state per hand |
| `app/gestures/state_machine.py` | Debounces static gestures — requires a dwell time before confirming, and won't re-fire the same gesture while it's held |
| `app/gestures/swipe_detector.py` | Tracks wrist Y-position over a rolling time window to detect downward motion |
| `app/controller/app_launcher.py` | Launches the app mapped to a gesture; checks running processes via `psutil` to avoid duplicates |
| `app/controller/window_controller.py` | Closes or minimizes the OS foreground window via `pywin32`; protects HandSense's own window |
| `app/config/gesture_mapping.py` | User-editable gesture-to-app mapping |

## Why MediaPipe's Tasks API (not `solutions`)

Early development used `mediapipe.solutions.hands`, but MediaPipe 1.x removed that legacy module entirely. The project now uses the `HandLandmarker` Tasks API, which requires a downloaded `.task` model file (see README installation steps) and reports results via `result.hand_landmarks` (a list of per-hand landmark lists) instead of `results.multi_hand_landmarks`.

## Finger State Detection

Rather than comparing a fingertip's vertical position to the joint below it (which breaks down when the hand is rotated or tilted relative to the camera), finger state is determined by **distance from a reference point**:

- **Index, middle, ring, pinky:** tip-to-wrist distance vs. base-joint-to-wrist distance. A finger is extended when its tip is farther from the wrist than its base joint is — true at any hand rotation.
- **Thumb:** uses the pinky's base joint (landmark 17) as the reference instead of the wrist, since the thumb folds *across* the palm rather than curling toward the wrist. This also removes the need to know which hand (left/right) is being read.

## Gesture Stability

A single frame's reading isn't trusted directly — the state machine requires a gesture to stay identical for a **dwell time** (default 1.0s) before it's confirmed, and once confirmed it enters a **held** state that won't re-fire the same gesture until the hand changes (a different gesture, or no hand). This prevents both flicker-triggered false positives and repeated firing from simply holding a pose.

## Swipe Detection

Unlike static poses, a swipe is inherently a motion over time. The detector keeps a short rolling history of (timestamp, wrist_y) samples, discards samples older than a time window (default 0.5s), and checks whether the wrist moved downward by more than a minimum distance within that window — only while the hand is read as an open palm, to avoid confusing incidental hand drift during other gestures with an intentional swipe.
'@ | Set-Content -Encoding UTF8 docs\architecture.md
powershell
@'
# Gesture Dictionary

| Gesture | Hand Configuration | Detection Method | Dwell / Window | Cooldown | Action | Notes |
|---|---|---|---|---|---|---|
| Number (1-3, extendable to 10) | Finger count via geometry | Distance-based per-finger state, summed across up to 2 hands | 1.0s hold | 1.0s (only between *different* gestures) | Launch mapped app | Skipped if app already running (checked via `psutil`) |
| Fist | 0 fingers extended | Same as above | 1.0s hold | 1.0s | Close active window | Self-protected — never closes HandSense's own window |
| Swipe down | Open palm (≥4 fingers), moving down | Rolling wrist-Y history over 0.5s window | N/A (motion-based) | 1.5s | Minimize active window | Requires open palm to avoid false triggers during other gestures |

## Design Notes

- **Why a minimum finger count for swipe:** without requiring an open palm, incidental downward hand drift during a different gesture (e.g. lowering the hand after a number gesture) could register as a swipe.
- **Why "held" gestures don't re-fire:** early testing showed that without this, holding a pose for longer than the cooldown period caused the same action to repeat every cooldown interval — undesirable for actions like opening an app.
- **Duplicate-open prevention:** rather than tracking which apps HandSense itself opened, the launcher checks the OS process list directly (`process_name` in the config) — this also correctly skips launch if the user opened the app manually.
