## Why

Orchestration output (stop/start/restart/rebuild) is only visible during the active operation. Once the user switches to a service log or starts a new operation, the previous output is lost from the UI. Users have no quick way to see what operations were performed and when without opening the raw log file.

## What Changes

- Add a helper function to parse `logs/orchestration.log` for operation headers (action type, services, timestamp)
- Add an `OrchestrationHistory` widget that displays the most recent operations in a compact list below the action buttons
- Show entries in reverse chronological order with relative timestamps (e.g., "Restarted webapp, worker — 2h ago")
- Limit display to the 5 most recent operations
- Refresh the history after each orchestration action completes and on dashboard startup
- Hide the history section when no operations have been performed

## Capabilities

### New Capabilities

_None — the `orchestration-history` spec already exists in `openspec/specs/orchestration-history/spec.md`._

### Modified Capabilities

- `tui-layout`: The actions column gains a new OrchestrationHistory widget below the action buttons

## Impact

- `stacktui/dashboard.py`: New `parse_orchestration_history()` function, new `OrchestrationHistory` widget class, layout changes in `compose()`, refresh calls in `_do_service_action()` and `on_mount()`
- No new dependencies — uses stdlib `re` and `datetime` for log parsing
- No breaking changes to existing functionality
