## Why

The dashboard currently shows all action buttons (Restart, Stop, Start) regardless of service state, and "Select All" is in the actions column separated from the service list. Users must manually select services after a git pull even though the dashboard already knows which services were affected. Unhealthy services are auto-checked but the selection controls and button visibility don't reflect the actual state of selected services.

## What Changes

- Auto-select services whose files changed after a git pull (persist affected services as app state)
- Show contextual action buttons based on selected service states:
  - All selected healthy/running → only Restart + Stop
  - All selected stopped → only Start
  - Mixed states → all three buttons
  - None selected → no buttons
- Move "Select All" checkbox below the service list into the services column
- Add "Changed" quick-select button (visible only when git pull detected affected services)
- Add "Unhealthy" quick-select button (visible only when unhealthy/stopped services exist)
- Lay out selection controls horizontally below the service list

## Capabilities

### New Capabilities

- `service-selection`: Smart service selection logic including auto-selection of affected/unhealthy services and quick-select controls (Changed, Unhealthy, Select All)

### Modified Capabilities

- `service-orchestration`: Action button visibility now depends on the state of selected services (contextual show/hide of Restart, Stop, Start)
- `tui-layout`: Selection controls move from actions column to below the service list in the services column
- `service-monitoring`: Expose per-service health state for querying by selection and button logic

## Impact

- **Code**: `dashboard.py` — ServicePanel, Dashboard.compose(), `_update_action_visibility()`, `_do_git_pull()`, `_refresh_status()`, CSS block
- **UI**: Actions column loses "Select All"; services column gains horizontal selection controls row; action buttons appear/disappear based on service state
- **No new dependencies**
