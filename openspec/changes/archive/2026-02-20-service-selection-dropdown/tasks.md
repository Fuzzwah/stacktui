## 1. Move Freshness Display

- [x] 1.1 In `ServicePanel.compose()`, move `yield Static("", id="data-freshness")` from after the service rows to before them (right after the "Services" title Static)

## 2. Replace Selection Controls with Dropdown

- [x] 2.1 In `Dashboard.compose()`, replace the `Horizontal(id="selection-controls")` block (containing Checkbox "All", Button "Changed", Button "Unhealthy") with a `Select` widget (`id="selection-mode"`) with options: All, Changed, Stopped, Running, None
- [x] 2.2 Remove CSS rules for `#selection-controls`, `#selection-controls Checkbox`, `#selection-controls Button`, `#btn-select-changed.hidden`, `#btn-select-unhealthy.hidden`
- [x] 2.3 Add CSS rule for `#selection-mode` (width: 100%, margin-top: 1)

## 3. Implement Selection Handler

- [x] 3.1 Add `@on(Select.Changed, "#selection-mode")` handler that: unchecks all services first, then checks the appropriate subset based on the selected value (all/changed/stopped/running/none), then resets the dropdown to blank
- [x] 3.2 Remove old handlers: `on_select_all_changed`, `on_select_changed_pressed`, `on_select_unhealthy_pressed`

## 4. Clean Up Refresh Logic

- [x] 4.1 In `_refresh_status()`, remove the show/hide logic for `#btn-select-changed` and `#btn-select-unhealthy` (lines ~1035-1046)

## 5. Update Git Pull Auto-Select

- [x] 5.1 In `_do_git_pull()`, keep the existing auto-check logic for affected services (no change needed — the dropdown is a command selector, not state)

## 6. Verify

- [x] 6.1 Run `uv run stacktui --dev` and confirm freshness appears above services
- [x] 6.2 Test each dropdown option: All, Changed, Stopped, Running, None
- [x] 6.3 Confirm action button visibility updates correctly after dropdown selection
