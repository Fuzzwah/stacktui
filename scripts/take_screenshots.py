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

from dashboard import Dashboard, find_config

OUTPUT_DIR = PROJECT_ROOT / "docs" / "screenshots"


async def take_screenshots(output_dir: Path) -> list[Path]:
    """Run the dashboard headlessly and capture screenshots in each theme."""
    output_dir.mkdir(parents=True, exist_ok=True)

    config = find_config(str(PROJECT_ROOT / "dashboard.toml"))
    app = Dashboard(config=config, prod=False)

    screenshots: list[Path] = []

    async with app.run_test(size=(120, 40), notifications=False) as pilot:
        # Wait for initial render and Docker status to populate
        await pilot.pause()
        await asyncio.sleep(4)

        # Check the "db" service checkbox so action buttons are visible
        await pilot.click("#chk-db")
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
