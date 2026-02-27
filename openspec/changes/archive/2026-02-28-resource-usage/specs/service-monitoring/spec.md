## MODIFIED Requirements

### Requirement: Health Status Display

Each service MUST display a colored status indicator with optional uptime, image tag, and resource usage.

#### Scenario: Healthy service

- GIVEN a service with health status "healthy"
- WHEN displayed in the ServicePanel
- THEN it shows a green dot with text "healthy"
- AND appends the uptime in dim style if available
- AND appends the image tag in dim style if the service is an infra service with a non-empty tag
- AND appends CPU% and memory usage in dim style if resource stats are available

#### Scenario: Running without healthcheck

- GIVEN a service in "running" state with no health status
- WHEN displayed in the ServicePanel
- THEN it shows a yellow dot with text "running"
- AND appends the uptime in dim style if available
- AND appends the image tag in dim style if the service is an infra service with a non-empty tag
- AND appends CPU% and memory usage in dim style if resource stats are available

#### Scenario: Stopped service

- GIVEN a service not found in Docker output
- WHEN displayed in the ServicePanel
- THEN it shows a dim dash "—"
- AND no uptime is displayed
- AND no image tag is displayed
- AND no resource usage is displayed

#### Scenario: Unhealthy service auto-selection

- GIVEN a service that transitions to an unhealthy/stopped state
- WHEN the status refresh detects this change
- THEN the service's checkbox is automatically checked

#### Scenario: High CPU usage warning

- GIVEN a running service using more than 80% CPU
- WHEN displayed in the ServicePanel
- THEN the CPU percentage is styled in warning color (yellow or red) instead of dim

#### Scenario: High memory usage warning

- GIVEN a running service using more than 80% of its memory limit
- WHEN displayed in the ServicePanel
- THEN the memory value is styled in warning color (yellow or red) instead of dim

### Requirement: Automatic Status Refresh

The system MUST refresh service status periodically.

#### Scenario: Refresh interval

- GIVEN the dashboard is mounted
- WHEN the refresh timer fires
- THEN `_refresh_status()` runs every 10 seconds
- AND updates the ServicePanel with current Docker state
- AND collects resource stats via `docker stats --no-stream --format json`
- AND checks for webhook signals
