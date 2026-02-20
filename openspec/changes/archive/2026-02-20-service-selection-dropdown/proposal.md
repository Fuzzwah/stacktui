## Why

The center pane's service selection controls (All checkbox, Changed button, Unhealthy button) render poorly — the buttons show with no visible text due to `height: 1` CSS, and the freshness indicator is buried below the service list where it's easy to miss. The selection UX needs to be cleaner and more discoverable.

## What Changes

- Move the "Freshness" status display from below the service list to above it (after the "Services" title)
- Remove the "All" checkbox, "Changed" button, and "Unhealthy" button
- Add a dropdown selector below the service list with options: All, Changed, Stopped, Running, None
- Selecting a dropdown option checks/unchecks the appropriate service checkboxes
- The dropdown is always visible (no show/hide logic based on state)

## Capabilities

### New Capabilities

_(none — this modifies existing capabilities)_

### Modified Capabilities

- `service-selection`: Replace checkbox + button controls with a Select dropdown; add Stopped and Running options
- `tui-layout`: Move freshness widget above service list; replace selection controls row with a Select dropdown

## Impact

- `stacktui/dashboard.py`: ServicePanel.compose(), Dashboard.compose(), CSS rules, selection event handlers, _refresh_status()
- No new dependencies
- No API changes
