## Why

The dashboard shows branch and SHA in the header but gives no indication of uncommitted local changes. Users need to know whether the working directory is clean before pulling or switching branches—dirty state can cause merge conflicts or lost work.

## What Changes

- Add a `get_git_status_summary()` helper that runs `git status --porcelain` and categorizes changes into modified, staged, and untracked counts
- Display a compact status summary (e.g., "3M 1S 2?" or "clean") next to the existing branch@SHA info in the header subtitle
- Style dirty state in yellow/warning color, clean state in green or omitted
- Refresh the git status summary on the existing 10-second timer and immediately after git operations (pull, checkout)

## Capabilities

### New Capabilities

- `git-status-summary`: Query, categorize, and display uncommitted working directory changes in the git info area

### Modified Capabilities

_(none — this adds new display content alongside existing git info without changing its behavior)_

## Impact

- **Code**: `stacktui/dashboard.py` — new helper function, changes to `get_git_info()` or subtitle rendering, updates to `_refresh_status()` and post-git-operation refresh points
- **Dependencies**: None (uses stdlib subprocess via existing `_run()`)
- **UI**: Header subtitle gains a short status indicator; no layout changes
