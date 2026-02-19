## 1. ServicePanel Health State Exposure

- [x] 1.1 Add `_service_statuses: dict[str, str]` to `ServicePanel.__init__()` and populate it in `update_services()` with each service's status_text (or empty string for missing services)
- [x] 1.2 Add `get_unhealthy_services() -> set[str]` method that returns services not "healthy"/"running"

## 2. Affected Service Tracking

- [x] 2.1 Add `self._affected_services: set[str] = set()` to `Dashboard.__init__()`
- [x] 2.2 In `_do_git_pull()`, store result of `detect_affected_services()` in `self._affected_services` and auto-select those services' checkboxes via `call_from_thread`
- [x] 2.3 In `_do_service_action()`, clear restarted services from `self._affected_services` after successful completion

## 3. Layout Changes

- [x] 3.1 Move "Select All" checkbox from `col-actions` to a new `Horizontal(id="selection-controls")` container placed after `ServicePanel` in `col-services`
- [x] 3.2 Add "Changed" button (`id="btn-select-changed"`, initially hidden) to selection controls row
- [x] 3.3 Add "Unhealthy" button (`id="btn-select-unhealthy"`, initially hidden) to selection controls row
- [x] 3.4 Remove "Select All" and related spacing from `col-actions`

## 4. Selection Control Event Handlers

- [x] 4.1 Add `on_select_changed_pressed` handler: check all services in `self._affected_services`
- [x] 4.2 Add `on_select_unhealthy_pressed` handler: check all services from `panel.get_unhealthy_services()`

## 5. Contextual Action Button Visibility

- [x] 5.1 Rewrite `_update_action_visibility()` to query selected services' states and show/hide individual buttons (Restart, Stop, Start) based on aggregate state
- [x] 5.2 Update `_refresh_status()` to toggle visibility of "Changed" and "Unhealthy" buttons based on current state

## 6. CSS Updates

- [x] 6.1 Add CSS for `#selection-controls` (horizontal layout, compact height, spacing)
- [x] 6.2 Style "Changed" and "Unhealthy" buttons to be compact/inline
- [x] 6.3 Add `.hidden` rules for the new buttons
- [x] 6.4 Update `col-actions` CSS to remove Select All related styles

## 7. Verification

- [ ] 7.1 Run dashboard with demo stack and verify selection controls appear below service list
- [ ] 7.2 Verify contextual button visibility changes based on selected service states
- [ ] 7.3 Verify "Changed" button appears after git pull with affected services
- [ ] 7.4 Verify "Unhealthy" button appears/hides based on service health

Note: 7.1-7.4 require interactive testing with `uv run python dashboard.py --dev`
