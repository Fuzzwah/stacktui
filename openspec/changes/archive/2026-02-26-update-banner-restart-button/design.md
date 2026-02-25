## Context

The `UpdateBanner` is currently a `Static` widget that renders a `Text` object with the message "StackTUI update available (N commits behind) — restart to update". It has no interactive elements. The app already has a "Reload Dashboard" button (`#btn-reload`) that calls `os.execv()` to re-exec the process, but that button lives in the actions column and only appears after a git pull updates the dashboard script — it does not pull updates itself.

## Goals / Non-Goals

**Goals:**
- Add a clickable "Restart to Update" button inside the UpdateBanner
- The button pulls the StackTUI repo then re-execs, combining fetch+restart into one action

**Non-Goals:**
- Changing the update detection logic (`_check_stacktui_updates`)
- Adding progress indicators during the pull/restart (the re-exec is near-instant)
- Changing the WebhookBanner (separate widget, different purpose)

## Decisions

### Convert UpdateBanner from Static to Horizontal

**Decision**: Change `UpdateBanner`'s base class from `Static` to `Horizontal` so it can contain both a `Static` text label and a `Button`.

**Rationale**: Textual's `Static` widget can only render text. To place a button alongside text, we need a container. `Horizontal` gives us side-by-side layout with minimal CSS. The text label uses `width: 1fr` to fill remaining space, pushing the button to the right.

**Alternative considered**: Keeping `Static` and using a click handler on the entire banner. Rejected because a visible button is a clearer affordance and consistent with the rest of the UI.

### Button handler does git pull then re-exec

**Decision**: The button press handler runs `git pull --ff-only` on the StackTUI repo (via `subprocess.run`) then calls `os.execv()` to restart.

**Rationale**: This reuses the exact same patterns as `_self_update()` (for the pull) and `#btn-reload` (for the re-exec). The pull is necessary because `_check_stacktui_updates` only fetches — it doesn't pull.

### Handler lives on Dashboard, not UpdateBanner

**Decision**: The `@on(Button.Pressed, "#btn-update-restart")` handler is defined on the `Dashboard` class, not inside `UpdateBanner`.

**Rationale**: This is consistent with all other button handlers in the app (`#btn-reload`, `#btn-restart`, etc.) which are defined on the `Dashboard` class. It also keeps `UpdateBanner` as a simple display widget.

## Risks / Trade-offs

- **[Risk] Pull fails (network/merge conflict)** → The `os.execv` still runs, effectively restarting without the update. This is acceptable — the banner will reappear on next check. Adding error handling for a rare edge case would over-complicate a simple flow.
