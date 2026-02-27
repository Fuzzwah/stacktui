## Why

The ServicePanel currently shows whether a service is running and its health status, but not how long it has been up. Container uptime is one of the most useful signals for day-to-day monitoring — a service showing "3d 4h" is stable, while one showing "2m" after an expected "3d" signals an unexpected restart. This information is already available in the `docker compose ps` JSON output but is not being extracted or displayed.

## What Changes

- Extend `ServiceInfo` to store container uptime (start time or duration)
- Extract the `Status` or `CreatedAt` field from `docker compose ps --format json` output in `parse_services()`
- Add a `format_uptime()` helper to render durations compactly (e.g., "3d 4h", "23m", "5s")
- Display uptime inline in each service row of the `ServicePanel`, after the status text
- Uptime refreshes every 10 seconds alongside existing service status polling

## Capabilities

### New Capabilities
- `container-uptime`: Extraction, formatting, and display of per-service container uptime in the ServicePanel

### Modified Capabilities
- `service-monitoring`: The `ServiceInfo` class and `parse_services()` function gain new fields for uptime data; the `ServicePanel` widget renders additional inline content per service row

## Impact

- **Code**: `stacktui/dashboard.py` — `ServiceInfo` class, `parse_services()`, `ServicePanel.update_services()`, and the service row rendering in `ServicePanel.compose()`/update logic
- **Dependencies**: None — uses data already returned by `docker compose ps`
- **UI**: Each service row becomes slightly wider; dimmed uptime text after status should not affect readability
