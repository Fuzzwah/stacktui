## Why

When the dashboard reloads or restarts, the log dropdown resets to the default service (first primary service). Users who prefer monitoring a specific log source (e.g., orchestration, a worker log file) must re-select it every time. The selected log should persist across sessions using the existing user preferences system.

## What Changes

- Save the selected log service to `.stacktui-user.toml` whenever the user changes the dropdown selection
- On startup, restore the last-selected log service from user preferences instead of falling back to the default
- If the saved selection is no longer available (service not running, log file removed), fall back to the existing default logic

## Capabilities

### New Capabilities

_(none — this extends existing capabilities)_

### Modified Capabilities

- `user-preferences`: Add a `[logs]` section with `selected` key for persisting the chosen log source
- `log-tailing`: Default log service selection should check user preferences before applying built-in default logic

## Impact

- `stacktui/dashboard.py`: `DashboardConfig` dataclass, `load_config()`, `_default_log_service()`, `on_service_changed()`, new `save_selected_log()` method
- `.stacktui-user.toml`: New `[logs]` section added when user changes log selection
