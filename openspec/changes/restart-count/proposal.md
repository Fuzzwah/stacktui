## Why

Containers can silently crash-loop — Docker's restart policy brings them back each time, but the dashboard only shows a green "running" status. Users have no visibility into restart-looping services without checking `docker inspect` manually. Surfacing the restart count directly in the service panel makes crash loops immediately visible.

## What Changes

- Add `restart_count` field to `ServiceInfo` by querying `docker inspect --format '{{.RestartCount}}'` for each container
- Display a restart indicator (e.g., "↻3") next to the service status when count > 0
- Color escalation: yellow for 1-4 restarts (warning), red for 5+ (critical restart loop)
- Auto-check services with 5+ restarts (same behavior as unhealthy services)
- Restart counts refresh alongside the existing 10-second status refresh cycle

## Capabilities

### New Capabilities
- `restart-count`: Query and display container restart counts with color-coded severity indicators

### Modified Capabilities
- `service-monitoring`: ServicePanel gains restart count badge display alongside existing status dots and uptime text
- `service-selection`: Services with high restart counts are auto-selected like unhealthy services

## Impact

- **Code**: `stacktui/helpers.py` — add restart count to `ServiceInfo` and `parse_services()`. `stacktui/widgets.py` — display badge in `update_services()`. `stacktui/app.py` — no changes needed (refresh loop already calls update_services).
- **Performance**: One additional `docker inspect` call per container during `parse_services()`, or batched via JSON format flag. Minimal overhead.
- **Dependencies**: None — uses only existing Docker CLI
