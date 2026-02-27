## Why

Users currently have to remember or look up which host port each Docker Compose service is exposed on. Displaying port mappings directly in the ServicePanel eliminates this friction and makes the dashboard a single pane of glass for service connectivity.

## What Changes

- Extract published port mappings from `docker compose ps --format json` output during service parsing
- Add a `ports` field to `ServiceInfo` to carry host port data
- Display host ports in a compact dimmed format (e.g., `:8000`) after the service status label in the ServicePanel
- Ports refresh automatically alongside existing service status polling

## Capabilities

### New Capabilities

_None — this is fully covered by the existing `port-mappings` spec._

### Modified Capabilities

- `port-mappings`: Implementing the existing spec that defines port extraction, display format, and refresh behavior
- `service-monitoring`: The `parse_services()` function and `ServiceInfo` object gain port data extraction, and the Health Status Display scenarios expand to include port display

## Impact

- `stacktui/dashboard.py`: `ServiceInfo` dataclass, `parse_services()`, `ServicePanel.update_services()` methods
- No new dependencies — port data is already present in `docker compose ps --format json` output
- No breaking changes to configuration or CLI interface
