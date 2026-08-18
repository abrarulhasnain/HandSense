# HandSense

Control your laptop using hand gestures detected through your webcam - no cursor, no touch. Show a number with your fingers to open an app, swipe to navigate or minimize, pinch to take a screenshot, or make a fist to close a window.

## Overview

HandSense reads hand landmarks in real time using MediaPipe and translates specific hand poses and motions into OS-level actions. Gesture recognition is entirely **rule-based geometry** - no trained classifier, no dataset - which keeps it fast, explainable, and easy to extend.

Every static gesture goes through a stability check before it fires: a pose has to hold steady for about a second before it's accepted, and each confirmed gesture only fires once until the hand changes, so nothing gets accidentally triggered or repeated by holding a pose. Motion gestures (swipes, pinch) use their own timing rules suited to how they're performed.

## Features (Working)

| Gesture | Trigger | Action |
|---|---|---|
| Finger count 1-10 (one hand for 1-5, both hands for 6-10) | Hold steady ~1s | Opens the mapped app - restores it to the foreground if it's already running/minimized |
| Fist (0 fingers) | Hold steady ~1s | Closes the active window (protects HandSense's own window) |
| Open palm, swipe down | Downward motion | Minimizes the active window |
| Open palm, swipe up | Upward motion | App switcher (Alt+Tab) |
| Open palm, swipe left/right | Sideways motion | Sends Left/Right Arrow (PDF page-turn, Netflix list navigation, etc.) |
| Pinch (thumb + index tip touch), quick tap | Brief touch and release | Takes a full-screen screenshot, with a flash overlay for visual confirmation |

Default app mapping: 1 Notepad, 2 Paint, 3 Calculator, 4 Chrome, 5 File Explorer, 6 WhatsApp, 7 VS Code, 8 GitHub Desktop, 9 Settings, 10 Task Manager - all defined in `app/config/gesture_mapping.py`, meant to be edited without touching any other code.

## In Progress (V2)

- [ ] Sustained pinch + vertical drag - volume control
- [ ] Both-hands-clasped - play/pause media
- [ ] Both-hands apart/together - zoom in/out
- [ ] Background/startup service (system tray, auto-start on boot)

## Why Rule-Based, Not ML

Finger states, pinches, and swipes are computed from landmark geometry (distances and relative positions between the 21 hand landmarks MediaPipe provides), not a trained classifier. This avoids needing a dataset or training step, keeps latency low, and makes every decision traceable back to a simple rule. A learned classifier may be introduced later only if user-trainable custom gestures are added.

## Architecture

Webcam (OpenCV)
-> MediaPipe HandLandmarker (21 landmarks per hand)
-> Finger State Extraction (distance-based geometry rules)
-> Gesture Recognition
- Static gestures (finger count / fist) -> Stability State Machine
- Motion gestures (swipe up/down/left/right) -> Rolling position history
- Pinch (screenshot tap) -> Normalized tip-distance + duration check
-> Action Dispatch (app launch/restore, window close/minimize, keyboard input, screenshot)
-> Debug Overlay (finger count, gesture status)


**Stability state machine** (for static gestures - finger counts, fist):

IDLE -> CANDIDATE (dwell timer running) -> HELD (confirmed, won't re-fire) -> IDLE (on release/change)


Static gesture confirmation is suppressed while the hand is actively moving or mid-pinch, so a swipe or pinch in progress doesn't get misread as a held number gesture.

See `docs/architecture.md` for the full breakdown and `docs/gestures.md` for gesture-by-gesture detection details.

## Project Structure

HandSense/
app/
camera/ - Webcam capture
vision/ - Hand detection + finger-state geometry
gestures/ - Stability state machine, swipe detector, pinch detector
controller/ - App launching, window control, keyboard actions, screenshots
ui/ - Reserved for future GUI/tray icon
config/ - Gesture to app mapping
utils/ - Reserved for shared helpers
tests/ - Reserved for automated tests
models/ - hand_landmarker.task (downloaded, not committed)
docs/ - Architecture and gesture documentation
main.py - Entry point
requirements.txt


## Tech Stack

| Purpose | Library |
|---|---|
| Hand detection & landmarks | MediaPipe (Tasks API - HandLandmarker) |
| Frame capture & processing | OpenCV |
| App launching / process check | os.startfile, psutil |
| Window close/minimize/restore | pywin32 |
| Keyboard simulation (arrows, Alt+Tab) | pynput |
| Screenshot capture + flash overlay | Pillow, tkinter |
| Numerical operations | NumPy |

## Installation

```powershell
git clone <your-repo-url>
cd HandSense

python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Download the hand landmark model (not committed to the repo - see .gitignore):

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "models\hand_landmarker.task"
```

## Running

```powershell
python main.py
```

A window opens showing the webcam feed with hand landmarks overlaid, current finger count, and gesture status. Press q to quit.

## Configuring App Mappings

Edit `app/config/gesture_mapping.py`:

```python
GESTURE_APP_MAP = {
    1: {"name": "Notepad", "path": "notepad.exe", "process_name": "notepad.exe"},
    # ...
}
```

- `path` accepts an executable name resolvable via Windows' App Paths, a full path (environment variables like %LOCALAPPDATA% are expanded), or a protocol URI (e.g. "ms-settings:").
- `process_name` is used to detect whether the app is already running, so a repeated gesture restores/focuses it instead of opening a duplicate.
- Set `"always_launch": True` for apps like File Explorer, where opening a new window each time is the expected behavior rather than a background process meaning "already open."

## Roadmap

- [x] Webcam capture pipeline
- [x] Hand detection + landmark overlay
- [x] Finger-state extraction (rotation-independent geometry)
- [x] Number-count gesture recognition (1-10, two hands)
- [x] Gesture stability (dwell time, no repeat-fire while held)
- [x] App launch with duplicate prevention + restore-on-repeat
- [x] Fist -> close active window (with self-protection)
- [x] Swipe down -> minimize active window
- [x] Swipe left/right -> page/list navigation
- [x] Swipe up -> app switcher
- [x] Pinch tap -> screenshot with flash feedback
- [ ] Sustained pinch -> volume control
- [ ] Two-hand gestures -> media play/pause, zoom
- [ ] Background/startup service with system tray icon
- [ ] Robustness testing across lighting/distance/background
- [ ] On-screen FPS + confidence overlay
- [ ] Packaging and polish

## Safety

- The system never targets its own window for close/minimize actions.
- No destructive file/system operations are performed - only launching apps, standard window close/minimize/restore signals, keyboard key presses, and screen capture.
- Every static gesture requires holding steady for a minimum duration before firing, to avoid accidental triggers from momentary hand movement. Motion-based gestures (swipes, pinch) use duration and movement thresholds tuned to avoid misreading incidental hand motion.

## License

MIT - see LICENSE file.

Save karke Notepad band karo.

docs/gestures.md bhi update karte hain — pinch + swipe-up add karo
powershell
notepad docs\gestures.md

Sab select-delete, ye paste karo:

markdown
# Gesture Dictionary

| Gesture | Hand Configuration | Detection Method | Dwell / Window | Cooldown | Action | Notes |
|---|---|---|---|---|---|---|
| Number (1-10) | Finger count via geometry, summed across up to 2 hands | Distance-based per-finger state | 1.0s hold | 1.0s (only between different gestures) | Launch mapped app, or restore/focus if already running | Suppressed while hand is moving or pinching |
| Fist | 0 fingers extended | Same as above | 1.0s hold | 1.0s | Close active window | Self-protected - never closes HandSense's own window |
| Swipe down | Open hand, moving down | Rolling palm-center position over 0.5s window | N/A (motion-based) | 1.0s | Minimize active window | No finger-count gate - motion itself is the signal |
| Swipe up | Open hand, moving up | Same as swipe down | N/A | 1.0s | App switcher (Alt+Tab) | Quick-switch behavior (jumps to last active app) |
| Swipe left/right | Open hand, moving sideways | Same as swipe down | N/A | 1.0s | Sends Left/Right Arrow key | Used for PDF page-turn, Netflix list navigation |
| Pinch tap | Thumb tip + index tip touch, released quickly | Tip distance normalized by hand size, checked against min/max hold duration | 0.15s-0.6s pinch duration | 1.0s | Takes a screenshot with a white flash overlay | Ignored while hand is in motion, to avoid false triggers during swipes |

## Default App Mapping

| Number | App |
|---|---|
| 1 | Notepad |
| 2 | Paint |
| 3 | Calculator |
| 4 | Chrome |
| 5 | File Explorer |
| 6 | WhatsApp |
| 7 | VS Code |
| 8 | GitHub Desktop |
| 9 | Settings |
| 10 | Task Manager |

## Design Notes

- **Why a minimum finger count isn't used for swipe anymore:** an earlier version required an open palm (4+ fingers) for swipes, but finger counts briefly fluctuate during fast hand motion due to camera perspective, causing missed detections. Swipes now track palm-center motion directly, with no finger-count requirement.
- **Why static gestures are suppressed during motion/pinch:** without this, a hand mid-swipe or mid-pinch could briefly read as a stable number pose and incorrectly launch an app.
- **Why pinch uses a normalized ratio:** raw tip-to-tip distance changes with how far the hand is from the camera. Dividing by the wrist-to-middle-finger-base distance (a proxy for hand size in the frame) keeps the pinch threshold consistent at any distance.
- **Why pinch has both a minimum and maximum duration:** a minimum duration filters out single-frame landmark jitter being misread as a pinch; a maximum duration distinguishes a quick "tap" (screenshot) from a sustained pinch (reserved for future gestures like volume control).
- **Duplicate-open prevention:** the launcher checks the OS process list directly (`process_name` in the config) rather than tracking what HandSense itself opened - this also correctly restores an app the user opened manually.
- **Restoring minimized windows:** `SetForegroundWindow` can be blocked by Windows for background processes without recent user input; a harmless simulated Alt key tap satisfies that check reliably before focusing the restored window.
