## Why

Users running StackTUI from a git clone have no way to know when a newer version is available upstream. The existing `_self_update()` only runs at startup and silently pulls — there's no in-app visibility into whether the tool itself is outdated. Adding an update check with a visible banner lets users know when updates are available without interrupting their workflow.

## What Changes

- Add a periodic background check that fetches the StackTUI repo and compares local HEAD against the upstream tracking branch
- Display an `UpdateBanner` widget when the local copy is behind upstream, showing how many commits behind
- Integrate the check into the dashboard refresh cycle (on a longer interval than service polling)
- Extend `_self_update()` to also update the StackTUI repo when it differs from the managed project

## Capabilities

### New Capabilities
- `self-update-check`: Background check for StackTUI repo updates with in-app banner notification

### Modified Capabilities
- `tui-layout`: Adding an UpdateBanner widget to the layout (new UI element in the top pane)

## Impact

- `stacktui/dashboard.py` — new helper functions, new widget class, layout and refresh loop changes
- Network: periodic `git fetch` calls to the StackTUI remote (every ~5 minutes)
- No new dependencies
