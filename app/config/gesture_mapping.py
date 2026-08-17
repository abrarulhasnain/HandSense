"""
Gesture-to-app mapping configuration.

Edit this dictionary to change which app opens for which finger count.
`path` is what gets launched; `process_name` is used to detect whether
the app is already running (so we don't open duplicates).
"""

GESTURE_APP_MAP = {
    1: {
        "name": "Notepad",
        "path": "notepad.exe",
        "process_name": "notepad.exe",
    },
    2: {
        "name": "Paint",
        "path": "mspaint.exe",
        "process_name": "mspaint.exe",
    },
    3: {
        "name": "Calculator",
        "path": "calc.exe",
        "process_name": "CalculatorApp.exe",  # Windows 11 calculator process name
    },
}
