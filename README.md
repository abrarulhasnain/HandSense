# Gesture Dictionary

| Gesture | Hand Configuration | Detection Method | Dwell / Window | Cooldown | Action | Notes |
|---|---|---|---|---|---|---|
| Number (1-10) | Finger count via geometry, summed across up to 2 hands | Distance-based per-finger state | 1.0s hold | 1.0s (only between different gestures) | Launch mapped app (see app/config/gesture_mapping.py) | Skipped if app already running (checked via psutil), unless always_launch is set |
| Fist | 0 fingers extended | Same as above | 1.0s hold | 1.0s | Close active window | Self-protected - never closes HandSense's own window |
| Swipe down | Open palm (4+ fingers), moving down | Rolling wrist-Y history over 0.5s window | N/A (motion-based) | 1.5s | Minimize active window | Requires open palm to avoid false triggers during other gestures |

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

- Why a minimum finger count for swipe: without requiring an open palm, incidental downward hand drift during a different gesture (e.g. lowering the hand after a number gesture) could register as a swipe.
- Why "held" gestures don't re-fire: early testing showed that without this, holding a pose for longer than the cooldown period caused the same action to repeat every cooldown interval - undesirable for actions like opening an app.
- Duplicate-open prevention: rather than tracking which apps HandSense itself opened, the launcher checks the OS process list directly (process_name in the config) - this also correctly skips launch if the user opened the app manually.
- os.startfile over subprocess.Popen: switched during the 1-10 mapping expansion because os.startfile resolves App Paths registry entries (like chrome.exe) and protocol URIs (like ms-settings:), which subprocess.Popen cannot.