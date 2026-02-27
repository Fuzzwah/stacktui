"""CLI entry point and self-update logic for StackTUI."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from . import helpers
from .config import PROJECT_ROOT
from .helpers import _get_stacktui_repo_root, _is_installed_package, find_config


# ---------------------------------------------------------------------------
# Self-update
# ---------------------------------------------------------------------------


def _self_update() -> None:
    """Pull latest code and re-exec if this script changed."""
    if _is_installed_package():
        return

    script = Path(__file__).resolve()
    old_mtime = script.stat().st_mtime

    # Pull the StackTUI repo if it differs from the managed project
    stacktui_repo = _get_stacktui_repo_root()
    if stacktui_repo and stacktui_repo != PROJECT_ROOT:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True, text=True, timeout=30, cwd=stacktui_repo,
        )
        if result.returncode != 0:
            print(f"StackTUI pull failed: {result.stderr.strip()}")

        if script.stat().st_mtime != old_mtime:
            print("StackTUI updated — restarting...")
            os.execv(sys.executable, [sys.executable, *sys.argv])

    # Pull the managed project
    result = subprocess.run(
        ["git", "pull", "--ff-only"],
        capture_output=True, text=True, timeout=30, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        print(f"git pull failed: {result.stderr.strip()}")
        return

    if result.stdout.strip() == "Already up to date.":
        return

    if script.stat().st_mtime != old_mtime:
        print("Dashboard updated — restarting...")
        os.execv(sys.executable, [sys.executable, *sys.argv])


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(description="StackTUI — Docker Compose Dashboard")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--prod", action="store_true", help="Force production mode")
    group.add_argument("--dev", action="store_true", help="Force development mode")
    parser.add_argument("--no-update", action="store_true", help="Skip self-update on startup")
    parser.add_argument("--config", type=str, default=None, help="Path to dashboard.toml config file")
    args = parser.parse_args()

    if not args.no_update:
        _self_update()

    config = find_config(args.config)

    # Set the global webhook signal file path
    helpers.WEBHOOK_SIGNAL_FILE = config.logs_dir / "github_push.json"

    if args.prod:
        prod: bool | None = True
    elif args.dev:
        prod = False
    else:
        prod = None

    # Ensure truecolor support so themes render correctly on all terminals
    os.environ.setdefault("COLORTERM", "truecolor")

    # Import here to avoid circular imports and speed up --help
    from .app import Dashboard

    app = Dashboard(config=config, prod=prod)
    app.run()


if __name__ == "__main__":
    main()
