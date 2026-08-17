"""
Gesture-to-app mapping configuration.

Edit this dictionary to change which app opens for which finger count.
`path` is what gets launched (can be an .exe name resolvable via Windows'
App Paths registry, a full path with %ENV_VARS%, or a protocol URI like
"ms-settings:"). `process_name` is used to detect whether the app is
already running, to avoid opening duplicates.

Set `always_launch: True` for apps where a "new instance" is the expected
behavior (like File Explorer opening a new window) rather than skipping
because a background process is already running.
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
        "process_name": "CalculatorApp.exe",
    },
    4: {
        "name": "Chrome",
        "path": "chrome.exe",
        "process_name": "chrome.exe",
    },
    5: {
        "name": "File Explorer",
        "path": "explorer.exe",
        "process_name": "explorer.exe",
        "always_launch": True,  # explorer.exe always has a background process; this opens a new window
    },
    6: {
        "name": "WhatsApp",
        "path": "whatsapp:",  # protocol URI - launches the installed Store app
        "process_name": "WhatsApp.exe",  # verify in Task Manager if this doesn't match
    },
    7: {
        "name": "VS Code",
        "path": r"%LOCALAPPDATA%\Programs\Microsoft VS Code\Code.exe",
        "process_name": "Code.exe",
    },
    8: {
        "name": "GitHub Desktop",
        "path": r"%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe",
        "process_name": "GitHubDesktop.exe",
    },
    9: {
        "name": "Settings",
        "path": "ms-settings:",
        "process_name": "SystemSettings.exe",
    },
    10: {
        "name": "Task Manager",
        "path": "Taskmgr.exe",
        "process_name": "Taskmgr.exe",
    },
}
