## 1. Log Parser

- [x] 1.1 Add `parse_orchestration_history()` function that reads the tail (~200 lines) of `logs/orchestration.log`, extracts operation headers via regex matching `=== Action [services] (timestamp) ===`, and returns the 5 most recent entries as a list of `(action, services_list, datetime)` tuples in reverse chronological order
- [x] 1.2 Add `_humanize_timedelta()` helper that converts a datetime delta to a compact relative string (e.g., "5m ago", "2h ago", "1d ago")

## 2. OrchestrationHistory Widget

- [x] 2.1 Create `OrchestrationHistory` widget (subclass of `Static`) that accepts a list of history entries and renders them as compact lines (e.g., "Restarted webapp, worker — 2h ago") with dim styling; hide the widget when the list is empty
- [x] 2.2 Add a `refresh_history()` method to `OrchestrationHistory` that calls `parse_orchestration_history()` and updates the widget content

## 3. Layout Integration

- [x] 3.1 Add the `OrchestrationHistory` widget to the actions column in `Dashboard.compose()`, below the Reload Dashboard button
- [x] 3.2 Call `refresh_history()` in `on_mount()` to populate history on startup

## 4. Refresh Triggers

- [x] 4.1 Call `refresh_history()` in the `finally` block of `_do_service_action()` after orchestration completes (via `call_from_thread`)
- [x] 4.2 Call `refresh_history()` in `_refresh_status()` so history updates on the 10-second refresh cycle
