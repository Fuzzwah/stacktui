## Context

The dashboard header subtitle currently shows `{mode} | {branch}@{sha}` via `get_git_info()`. This is set on mount and updated after git pull/checkout operations. There is no visibility into uncommitted working directory state, which matters when deciding whether to pull or switch branches.

The subtitle is rendered in 4 places: `on_mount`, `_refresh_status` (not currently—but should be for live updates), `_do_git_pull` finally block, and `_do_checkout` on success. The `_refresh_status` method runs on a 10-second interval timer.

## Goals / Non-Goals

**Goals:**
- Show a compact working-tree summary alongside existing branch@sha info in the header subtitle
- Keep it lightweight—`git status --porcelain` is fast and safe
- Refresh automatically on the existing timer and after git operations

**Non-Goals:**
- Detailed file-level change listing (this is a summary indicator only)
- Blocking or warning dialogs before pull/checkout (visual indicator is sufficient)
- Tracking stashed changes or submodule status

## Decisions

### 1. New `get_git_status_summary()` helper function

Add a standalone module-level function (like the existing `get_git_info()`) that runs `git status --porcelain` via `_run()` and returns a formatted summary string.

**Rationale**: Follows the existing pattern of module-level helper functions. Keeps the logic testable and separate from the widget layer.

**Alternative considered**: Modifying `get_git_info()` directly. Rejected because the functions have different purposes (identity vs. state) and combining them makes the return value harder to use independently.

### 2. Porcelain output parsing

Parse the two-character status codes from `git status --porcelain` to categorize:
- **Staged**: first character is `M`, `A`, `D`, `R`, or `C`
- **Modified**: second character is `M` or `D`
- **Untracked**: status is `??`

Return a compact string like `"3M 1S 2?"` for dirty state or `"clean"` for empty output.

**Rationale**: Porcelain format is stable across git versions and simple to parse. The compact format mirrors conventions users are familiar with from shell prompts.

### 3. Subtitle integration pattern

Append the status summary to the existing subtitle: `"{mode} | {branch}@{sha} | {status_summary}"`. When clean, either show `"clean"` or omit the segment entirely to reduce noise.

**Rationale**: Minimal change—just extends the existing subtitle string. No new widgets or layout changes needed.

### 4. Refresh in `_refresh_status()`

Call `get_git_status_summary()` inside `_refresh_status()` and update `self.sub_title`. This piggybacks on the existing 10-second interval.

**Rationale**: Avoids a separate timer. The git status query is fast (<50ms for typical repos). The subtitle is already updated after git pull/checkout; adding it to the refresh loop closes the gap for external changes.

## Risks / Trade-offs

- **[Performance in large repos]** → `git status --porcelain` can be slow in very large repos with many untracked files. Mitigation: the existing `_run()` timeout applies; worst case the summary shows empty/stale.
- **[Subtitle length]** → Adding more text to the subtitle could overflow on narrow terminals. Mitigation: the summary is compact (max ~15 chars like "99M 99S 99?"), and Textual truncates gracefully.
