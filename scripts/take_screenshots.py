#!/usr/bin/env python3
"""Generate themed screenshots of the StackTUI dashboard.

Usage:
    uv run python scripts/take_screenshots.py [--output-dir docs/screenshots]

Requires demo Docker services to be running:
    docker compose -f demo/docker-compose.yml up -d
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from rich.text import Text
from textual.widgets import Button, RichLog, Select

from stacktui.dashboard import Dashboard, find_config
from stacktui.widgets import UpdateBanner, WebhookBanner

OUTPUT_DIR = PROJECT_ROOT / "docs" / "screenshots"


async def take_screenshots(output_dir: Path) -> list[Path]:
    """Run the dashboard headlessly and capture screenshots in each theme."""
    output_dir.mkdir(parents=True, exist_ok=True)

    config = find_config(str(PROJECT_ROOT / "dashboard.toml"))
    app = Dashboard(config=config, prod=False)

    screenshots: list[Path] = []

    async with app.run_test(size=(160, 50), notifications=False) as pilot:
        # Wait for initial render and Docker status to populate
        await pilot.pause()
        await asyncio.sleep(4)

        # Check the "db" service checkbox so action buttons are visible
        await pilot.click("#chk-db")
        await pilot.pause()

        # Override _update_action_visibility so the periodic refresh doesn't
        # reset our manual button state during screenshot capture, then
        # force the correct state: Stop/Restart/Rebuild visible, Start hidden
        # (selected service is healthy/running).
        def _noop_visibility() -> None:
            pass
        app._update_action_visibility = _noop_visibility  # type: ignore[assignment]

        for btn_id in ("#btn-stop", "#btn-restart", "#btn-rebuild"):
            app.query_one(btn_id, Button).remove_class("hidden")
        app.query_one("#btn-start", Button).add_class("hidden")

        # Allow a couple of event loop cycles so the class changes take effect
        await pilot.pause()
        await pilot.pause()

        # Show mock "StackTUI update available" banner and webhook notification
        update_banner = app.query_one("#update-banner", UpdateBanner)
        update_banner.show_update(3)

        webhook = app.query_one("#webhook-banner", WebhookBanner)
        webhook.show_push({
            "pusher": "dependabot",
            "commits": [
                {"message": "Bump flask from 3.0.2 to 3.1.0"},
                {"message": "Update redis dependency to 7.2"},
                {"message": "Fix healthcheck timeout in docker-compose"},
            ],
        })
        await pilot.pause()

        # Cancel any running log tail and replace with mock output so
        # screenshots look clean even when Docker isn't available.
        if app._log_task and not app._log_task.done():
            app._log_task.cancel()
        if app._log_process and app._log_process.returncode is None:
            app._log_process.terminate()
        log_view = app.query_one("#log-view", RichLog)
        log_view.clear()
        # Update the dropdown to show "Web App" without triggering a new tail
        svc_select = app.query_one("#service-select", Select)
        with app.prevent(Select.Changed):
            svc_select.value = "webapp"
        log_view.write(Text("--- Tailing Web App ---", style="dim italic"))
        log_view.write("webapp-1  |  * Running on http://0.0.0.0:5000")
        log_view.write("webapp-1  |  [INFO] Starting worker [pid: 42]")
        log_view.write('webapp-1  |  GET /health 200 — 1ms')
        log_view.write('webapp-1  |  GET / 200 — 12ms')
        log_view.write('webapp-1  |  GET /api/status 200 — 3ms')
        await pilot.pause()

        themes = sorted(app.available_themes)
        print(f"  Found {len(themes)} themes: {', '.join(themes)}")

        for theme_name in themes:
            app.theme = theme_name
            await pilot.pause()
            await asyncio.sleep(0.5)

            filename = f"{theme_name}.svg"
            filepath = output_dir / filename
            app.save_screenshot(filename=filename, path=str(output_dir))
            screenshots.append(filepath)
            print(f"  Captured: {filename}")

    return screenshots


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate StackTUI themed screenshots")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help="Directory to save screenshots (default: docs/screenshots)",
    )
    args = parser.parse_args()

    paths = asyncio.run(take_screenshots(args.output_dir))
    print(f"\nGenerated {len(paths)} screenshots in {args.output_dir}")


if __name__ == "__main__":
    main()
