## Why

The dashboard currently shows service status (running/stopped/unhealthy) but provides no visibility into resource consumption. Users must leave the TUI and run `docker stats` separately to check for runaway CPU or memory leaks. Adding resource usage display enables early detection of problems without context-switching.

## What Changes

- Add a `get_resource_stats()` helper that calls `docker stats --no-stream --format json` to collect CPU and memory usage for all containers in a single call
- Extend `_refresh_status()` to collect resource stats alongside service status on each 10-second refresh cycle
- Update `ServicePanel` to display compact resource usage (CPU% and memory) next to each running service's status dot
- Format memory in human-readable units (e.g., "384M", "2.3G")
- Style high resource usage (>80% CPU or memory) with warning colors (yellow/red)
- Show no resource data for stopped services
- Gracefully degrade when `docker stats` fails or times out (show "—" or clear values)

## Capabilities

### New Capabilities

_None — the `resource-usage` spec already exists._

### Modified Capabilities

- `service-monitoring`: The ServicePanel display needs to accommodate resource usage values alongside existing status indicators

## Impact

- **Code**: `stacktui/dashboard.py` — new helper function, changes to `_refresh_status()` and `ServicePanel` widget
- **Performance**: One additional `docker stats --no-stream` call per refresh cycle (completes in ~1-2s)
- **Dependencies**: None — uses Docker CLI already available
