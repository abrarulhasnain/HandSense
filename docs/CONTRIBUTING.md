# Contributing to HandSense

Quick guide to get set up and start working on this project.

## 1. Get Access

- You're a member of the `HandSense-Team` GitHub organization - accept the invite email/notification if you haven't.
- Repo: https://github.com/HandSense-Team/HandSense

## 2. Clone the Repo

```powershell
git clone https://github.com/HandSense-Team/HandSense.git
cd HandSense
```

## 3. Set Up Your Environment

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Download the hand-tracking model (not stored in the repo):

```powershell
Invoke-WebRequest -Uri "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task" -OutFile "models\hand_landmarker.task"
```

## 4. Run It

```powershell
python main.py
```

Webcam window opens. Press `q` to quit.

## 5. Project Layout (Where Things Live)

| Folder | What's in it |
|---|---|
| `app/camera/` | Webcam capture |
| `app/vision/` | Hand detection, finger counting |
| `app/gestures/` | Gesture stability logic, swipe/pinch detection |
| `app/controller/` | Actual actions - open apps, close/minimize windows, keyboard, screenshots |
| `app/config/` | Gesture-to-app mapping (edit this to change what opens) |
| `docs/` | Architecture and gesture documentation |
| `main.py` | Everything connects here |

Read `docs/architecture.md` and `docs/gestures.md` before changing gesture logic.

## 6. Making Changes

1. Make sure you're up to date first:
```powershell
   git pull origin main
```
2. Make your changes, test with `python main.py`.
3. Commit and push (GitHub Desktop works too):
```powershell
   git add .
   git commit -m "short description of what you changed"
   git push origin main
```
4. For bigger changes, prefer a branch + pull request instead of pushing straight to `main`:
```powershell
   git checkout -b your-feature-name
   git push origin your-feature-name
```
   Then open a Pull Request on GitHub so it can be reviewed before merging.

## 7. Ground Rules

- Rule-based logic only (no ML/training) - this is a deliberate V1 design choice.
- Every new gesture needs a stability/timing check (dwell time, cooldown, or motion threshold) to avoid false triggers - look at `app/gestures/state_machine.py` or `swipe_detector.py` for the pattern.
- Never let a gesture target HandSense's own window - see `PROTECTED_WINDOW_TITLES` in `app/controller/window_controller.py`.
- Test manually before pushing - there's no automated test suite yet.

## Current Status

V1 complete: number gestures (1-10) open apps, fist closes windows, swipes navigate/minimize, pinch-tap takes screenshots.

In progress: sustained-pinch volume control, two-hand gestures, background/tray app mode.