# Log Error Count Specification

## Purpose

Display a count of recent ERROR and CRITICAL log lines per service as a badge on the service row. Surfaces problems without requiring the user to manually tail each service's logs.

## Requirements

### Requirement: Error Line Detection

The system MUST scan recent container logs for error-level entries.

#### Scenario: Count errors in Docker logs

- GIVEN a running service with Docker logs
- WHEN scanning for errors
- THEN the system runs `docker compose logs --tail=100 <service>` for each service
- AND counts lines matching error patterns (ERROR, CRITICAL, FATAL, PANIC) case-insensitively

#### Scenario: No errors found

- GIVEN a service with no error lines in recent logs
- WHEN scanning for errors
- THEN the error count is 0
- AND no badge is displayed

#### Scenario: Service not running

- GIVEN a service that is not running
- WHEN scanning for errors
- THEN no log scan is performed
- AND no error badge is shown

### Requirement: Error Badge Display

The error count MUST be shown as a visible badge when errors exist.

#### Scenario: Low error count

- GIVEN a service with 3 error lines in recent logs
- WHEN displayed in the ServicePanel
- THEN a badge shows the count (e.g., "3 err") next to the service status
- AND the badge is styled in yellow

#### Scenario: High error count

- GIVEN a service with 20 or more error lines in recent logs
- WHEN displayed in the ServicePanel
- THEN a badge shows the count (e.g., "20+ err")
- AND the badge is styled in red to signal a serious problem

#### Scenario: Zero errors

- GIVEN a service with no errors in recent logs
- WHEN displayed in the ServicePanel
- THEN no error badge is shown
- AND the service row layout is unchanged

### Requirement: Error Pattern Configuration

The error detection patterns SHOULD be configurable.

#### Scenario: Default patterns

- GIVEN no custom error patterns in `dashboard.toml`
- WHEN scanning logs
- THEN the system uses default patterns: `ERROR`, `CRITICAL`, `FATAL`, `PANIC`
- AND matching is case-insensitive

#### Scenario: Custom patterns via config

- GIVEN `[logs].error_patterns = ["ERROR", "Exception", "WARN"]` in config
- WHEN scanning logs
- THEN the system uses the configured patterns instead of defaults

### Requirement: Error Count Refresh

Error counts MUST be refreshed periodically.

#### Scenario: Refresh on timer

- GIVEN the dashboard refresh timer fires
- WHEN `_refresh_status()` runs
- THEN error counts are re-scanned for all running services
- AND the ServicePanel updates badges accordingly

#### Scenario: Performance consideration

- GIVEN many running services
- WHEN scanning logs for error counts
- THEN the scan uses `--tail=100` to limit the amount of log data processed
- AND the scan does not block the UI or significantly delay the refresh cycle

#### Scenario: Count reflects recent window

- GIVEN a service that had errors an hour ago but has been clean since
- WHEN scanning the last 100 log lines
- THEN the error count reflects only the recent log window
- AND old errors that have scrolled past the tail limit are not counted
