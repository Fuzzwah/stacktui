---
name: "Update Docs"
description: Update README.md from OpenSpec specs and generate themed screenshots
category: Docs
tags: [docs, screenshots, readme]
---

Update the project README.md to match the current feature set (sourced from OpenSpec specs) and generate themed screenshots of the demo environment.

**Input**: Optional argument after `/update-docs`:
- No argument: run both screenshots and README update
- `screenshots-only`: only generate screenshots
- `readme-only`: only update README (assumes screenshots already exist)

---

## Phase 1: Pre-flight

1. **Check Docker is running:**
   ```bash
   docker info > /dev/null 2>&1
   ```
   If Docker is not running, stop and tell the user.

2. **Check if demo services are up:**
   ```bash
   docker compose -f demo/docker-compose.yml ps --format json
   ```
   If not running, start them:
   ```bash
   docker compose -f demo/docker-compose.yml up -d
   ```
   Wait up to 60 seconds for services to become healthy before proceeding.

---

## Phase 2: Generate Screenshots (skip if `readme-only`)

1. **Run the screenshot script:**
   ```bash
   uv run python scripts/take_screenshots.py
   ```

2. **Verify output** — check that SVG files exist in `docs/screenshots/`.

3. Report which themes were captured.

---

## Phase 3: Update README.md (skip if `screenshots-only`)

1. **Read all source material:**
   - All spec files: `openspec/specs/*/spec.md`
   - Current keyboard bindings: the `BINDINGS` class variable in `dashboard.py`
   - Configuration reference: `dashboard.toml.example`
   - Dependencies: `pyproject.toml`
   - Demo services: `demo/docker-compose.yml`
   - Available screenshots: `docs/screenshots/*.svg`

2. **Rewrite README.md** using the following section structure and source mapping:

   | Section | Source | Notes |
   |---------|--------|-------|
   | Title + tagline | `pyproject.toml` description | |
   | Screenshots/Themes | `docs/screenshots/` | Gallery of theme previews |
   | Features | All spec `## Purpose` sections | One bullet per major capability |
   | Quick Start | Preserve existing content | Static instructions |
   | Use With Your Project | Preserve existing content | Static instructions |
   | Keyboard Shortcuts | `dashboard.py` BINDINGS | Table of all bindings |
   | Configuration | configuration spec + `dashboard.toml.example` | Key sections list |
   | Demo Environment | `demo/docker-compose.yml` | Service table |
   | Requirements | `pyproject.toml` + specs | Python, Docker, Git |
   | License | Preserve existing | |

3. **Feature extraction rules:**
   - Every feature listed MUST trace to a requirement in a spec file
   - If a spec has a requirement not reflected in the README, add it
   - If the README mentions something not in any spec, flag it for the user
   - Keep descriptions concise — specs have the detail, README is the summary

4. **Screenshot gallery format:**
   Use a table or image grid showing 2-4 themes as highlights, with a note that more themes are available. Example:
   ```markdown
   ### Themes

   StackTUI supports multiple color themes. Press `T` to cycle through them.

   | | |
   |---|---|
   | ![textual-dark](docs/screenshots/textual-dark.svg) | ![nord](docs/screenshots/nord.svg) |
   | ![gruvbox](docs/screenshots/gruvbox.svg) | ![tokyo-night](docs/screenshots/tokyo-night.svg) |
   ```

---

## Phase 4: Summary

After completing, show:
- List of screenshots generated (if applicable)
- Summary of README changes (sections added/updated)
- Reminder: "Review the changes and commit when ready."

---

## Guardrails

- Do NOT invent features — every feature must come from a spec
- Do NOT modify the Quick Start or Use With Your Project sections unless they reference outdated commands
- Do NOT commit changes — leave that to the user
- If demo services fail to start, skip screenshots but still update README (note missing screenshots)
- Keep the README concise and scannable
