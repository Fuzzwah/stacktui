## Why

Services can fail silently — errors and exceptions pile up in container logs but the dashboard only shows a healthy/running status dot. Users must manually tail each service's logs to discover problems. Adding an error count badge to the service panel surfaces issues at a glance, reducing mean-time-to-detection for production problems.

## What Changes

- Add a new helper function that scans recent Docker logs (`--tail=100`) for error-level patterns (ERROR, CRITICAL, FATAL, PANIC)
- Display an error count badge (e.g., "3 err") next to each service's status indicator in the ServicePanel
- Badge color escalates: yellow for low counts, red for 20+ errors
- Error counts refresh alongside the existing 10-second status refresh cycle
- Add optional `[logs].error_patterns` config for custom error pattern overrides

## Capabilities

### New Capabilities
- `log-error-count`: Scan recent container logs for error patterns and display per-service error count badges in the ServicePanel

### Modified Capabilities
- `service-monitoring`: ServicePanel gains error badge display alongside existing status dots and uptime text

## Impact

- **Code**: `stacktui/dashboard.py` — new `get_error_counts()` helper, changes to `ServicePanel.update_services()` and `_refresh_status()`
- **Config**: `dashboard.toml` — optional `[logs].error_patterns` list
- **Performance**: One `docker compose logs --tail=100 <service>` call per running service per refresh cycle; mitigated by the small tail window
- **Dependencies**: None — uses only stdlib and existing Docker CLI
