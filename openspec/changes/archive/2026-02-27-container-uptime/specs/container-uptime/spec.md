## ADDED Requirements

### Requirement: Uptime Data Extraction

The system MUST extract container uptime from the `docker compose ps --format json` Status field during service parsing.

#### Scenario: Parse uptime from running container

- **WHEN** `parse_services()` processes a JSON line with `Status` containing "Up 3 hours"
- **THEN** it extracts the duration and stores `uptime_seconds` on the `ServiceInfo` object

#### Scenario: Parse uptime with days

- **WHEN** `parse_services()` processes a JSON line with `Status` containing "Up 2 days"
- **THEN** `uptime_seconds` is set to approximately 172800

#### Scenario: Stopped container has no uptime

- **WHEN** `parse_services()` processes a container with `State` "exited" or missing
- **THEN** `uptime_seconds` is `None`

#### Scenario: Unparseable status string

- **WHEN** the `Status` field has an unexpected format that cannot be parsed
- **THEN** `uptime_seconds` is `None`
- **THEN** the dashboard continues to function normally without uptime display

### Requirement: Compact Duration Formatting

The system MUST format uptime as a compact human-readable string.

#### Scenario: Seconds only

- **WHEN** uptime is 45 seconds
- **THEN** `format_uptime()` returns "45s"

#### Scenario: Minutes

- **WHEN** uptime is 1380 seconds (23 minutes)
- **THEN** `format_uptime()` returns "23m"

#### Scenario: Hours and minutes

- **WHEN** uptime is 20520 seconds (5 hours 42 minutes)
- **THEN** `format_uptime()` returns "5h 42m"

#### Scenario: Days and hours

- **WHEN** uptime is 273600 seconds (3 days 4 hours)
- **THEN** `format_uptime()` returns "3d 4h"

#### Scenario: Days only when no remaining hours

- **WHEN** uptime is 1209600 seconds (14 days exactly)
- **THEN** `format_uptime()` returns "14d"

### Requirement: Uptime Display in ServicePanel

The system MUST display uptime inline in each service row after the status text.

#### Scenario: Running service with uptime

- **WHEN** `update_services()` renders a service with `uptime_seconds` set
- **THEN** the uptime text is appended after the status text on the same line
- **THEN** the uptime text is styled with `dim` to be visually subordinate

#### Scenario: Stopped or missing service

- **WHEN** `update_services()` renders a service with `uptime_seconds` as `None`
- **THEN** no uptime text is appended
- **THEN** the service row displays identically to current behavior

### Requirement: Uptime Refresh

The system MUST update uptime values on every status refresh cycle.

#### Scenario: Uptime updates on refresh

- **WHEN** `_refresh_status()` fires on the 10-second interval
- **THEN** `parse_services()` re-extracts uptime from fresh Docker output
- **THEN** the `ServicePanel` displays the updated uptime values

#### Scenario: Restart resets uptime

- **WHEN** a container restarts between refresh cycles
- **THEN** the next refresh shows a small uptime value (seconds or minutes)
- **THEN** the drop in uptime visually signals the restart
