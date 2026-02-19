#!/usr/bin/env python3
"""Write a fake GitHub webhook signal file to trigger the dashboard banner.

Run this to simulate a GitHub push notification:

    python demo/send_webhook.py
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
SIGNAL_FILE = LOGS_DIR / "github_push.json"


def get_current_branch() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() or "main"
    except Exception:
        return "main"


def main() -> None:
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

    signal = {
        "branch": get_current_branch(),
        "after": "0" * 40,  # Fake SHA that won't match local HEAD
        "pusher": "demo-user",
        "commits": [
            {
                "message": "Update worker logging format",
                "id": "abc1234",
                "timestamp": datetime.now().isoformat(),
            },
            {
                "message": "Fix nginx proxy headers",
                "id": "def5678",
                "timestamp": datetime.now().isoformat(),
            },
        ],
    }

    SIGNAL_FILE.write_text(json.dumps(signal, indent=2))
    print(f"Wrote webhook signal to {SIGNAL_FILE}")
    print("The dashboard will show the notification banner on its next refresh (within 10s).")


if __name__ == "__main__":
    main()
