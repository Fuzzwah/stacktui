## 1. Configuration

- [x] 1.1 Add `error_patterns: list[str]` field to `DashboardConfig` with default `["ERROR", "CRITICAL", "FATAL", "PANIC"]`
- [x] 1.2 Parse `[logs].error_patterns` from `dashboard.toml` in the config loader
- [x] 1.3 Add `error_patterns` example to `dashboard.toml.example` under `[logs]`

## 2. Error Scanning Helper

- [x] 2.1 Add `get_error_counts(config, compose_file, running_services) -> dict[str, int]` module-level function
- [x] 2.2 For each running service, run `docker compose logs --tail=100 <service>` and count lines matching any pattern (case-insensitive)
- [x] 2.3 Return dict mapping service name to error count (0 for no errors, skip non-running services)

## 3. ServicePanel Badge Display

- [x] 3.1 Update `ServicePanel.update_services()` to accept an `error_counts: dict[str, int]` parameter
- [x] 3.2 For services with error count > 0 and < 20, append yellow badge `" N err"` to the status Text
- [x] 3.3 For services with error count >= 20, append red badge `" 20+ err"` to the status Text
- [x] 3.4 For services with error count 0 or not running, append nothing

## 4. Refresh Loop Integration

- [x] 4.1 In `_refresh_status()`, call `get_error_counts()` with the list of running service names from `parse_services()`
- [x] 4.2 Pass the error counts dict to `panel.update_services()`

## 5. Testing

- [x] 5.1 Verify error badges appear for services with errors in the demo environment
- [x] 5.2 Verify no badge appears for healthy services with clean logs
- [x] 5.3 Verify custom `error_patterns` config override works
