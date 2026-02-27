## Why

Users currently have no way to see which Docker image version each service is running without manually running `docker inspect` commands. For infrastructure services like postgres and redis, knowing the running version is critical for debugging compatibility issues and planning upgrades.

## What Changes

- Add image tag extraction to the service status refresh cycle
- Display image version tags (e.g., `:16.2`, `:7.4`) next to infrastructure service labels in the ServicePanel
- Truncate long registry prefixes, showing only the tag portion
- Skip version display for locally-built primary services and stopped services

## Capabilities

### New Capabilities

- `image-versions`: Extract and display Docker image tags next to service names in the ServicePanel, with smart formatting for infra vs primary services

### Modified Capabilities

- `service-monitoring`: The `ServiceInfo` object and `parse_services()` must capture image name/tag data; `ServicePanel.update_services()` must render image tags inline

## Impact

- `stacktui/dashboard.py`: `ServiceInfo` class gains an `image` field; `parse_services()` extracts image from JSON output; `ServicePanel.update_services()` renders tag text
- No new dependencies required — all data comes from existing `docker compose ps --format json` output
