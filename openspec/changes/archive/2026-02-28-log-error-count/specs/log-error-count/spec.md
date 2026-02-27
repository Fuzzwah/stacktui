## ADDED Requirements

### Requirement: Error Line Detection

The system MUST scan recent container logs for error-level entries.

#### Scenario: Count errors in Docker logs

- **WHEN** scanning for errors on a running service
- **THEN** the system runs `docker compose logs --tail=100 <service>` for each service
- **AND** counts lines matching error patterns (ERROR, CRITICAL, FATAL, PANIC) case-insensitively

#### Scenario: No errors found

- **WHEN** a service has no error lines in recent logs
- **THEN** the error count is 0
- **AND** no badge is displayed

#### Scenario: Service not running

- **WHEN** a service is not running
- **THEN** no log scan is performed
- **AND** no error badge is shown

### Requirement: Error Badge Display

The error count MUST be shown as a visible badge when errors exist.

#### Scenario: Low error count

- **WHEN** a service has between 1 and 19 error lines in recent logs
- **THEN** a badge shows the count (e.g., "3 err") next to the service status
- **AND** the badge is styled in yellow

#### Scenario: High error count

- **WHEN** a service has 20 or more error lines in recent logs
- **THEN** a badge shows the count (e.g., "20+ err")
- **AND** the badge is styled in red

#### Scenario: Zero errors

- **WHEN** a service has no errors in recent logs
- **THEN** no error badge is shown
- **AND** the service row layout is unchanged

### Requirement: Error Pattern Configuration

The error detection patterns MUST be configurable.

#### Scenario: Default patterns

- **WHEN** no custom error patterns are configured in `dashboard.toml`
- **THEN** the system uses default patterns: `ERROR`, `CRITICAL`, `FATAL`, `PANIC`
- **AND** matching is case-insensitive

#### Scenario: Custom patterns via config

- **WHEN** `[logs].error_patterns = ["ERROR", "Exception", "WARN"]` is set in config
- **THEN** the system uses the configured patterns instead of defaults

### Requirement: Error Count Refresh

Error counts MUST be refreshed periodically.

#### Scenario: Refresh on timer

- **WHEN** the dashboard refresh timer fires
- **THEN** error counts are re-scanned for all running services
- **AND** the ServicePanel updates badges accordingly

#### Scenario: Performance consideration

- **WHEN** scanning logs for error counts
- **THEN** the scan uses `--tail=100` to limit the amount of log data processed
- **AND** the scan does not block the UI or significantly delay the refresh cycle
