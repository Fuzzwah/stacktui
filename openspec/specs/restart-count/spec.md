# Restart Count Specification

## Purpose

Display the number of times each container has restarted, highlighting services that are restart-looping. A silently crashing and restarting container is a common failure mode that is otherwise invisible in the dashboard.

## Requirements

### Requirement: Restart Count Query

The system MUST query Docker for each container's restart count.

#### Scenario: Query restart count via docker inspect

- GIVEN running Docker Compose services
- WHEN the refresh cycle runs
- THEN the system queries `docker inspect --format '{{.RestartCount}}' <container>` for each service
- AND stores the restart count in the `ServiceInfo` object

#### Scenario: Container not found

- GIVEN a configured service with no running container
- WHEN querying restart count
- THEN the restart count is treated as 0 or unavailable
- AND no error is raised

### Requirement: Restart Count Display

The restart count MUST be shown when greater than zero.

#### Scenario: No restarts

- GIVEN a service with a restart count of 0
- WHEN displayed in the ServicePanel
- THEN no restart count indicator is shown
- AND the service row appears unchanged from current behavior

#### Scenario: Low restart count

- GIVEN a service with a restart count between 1 and 4
- WHEN displayed in the ServicePanel
- THEN it shows a restart indicator (e.g., "↻1") next to the status
- AND the indicator is styled in yellow as a warning

#### Scenario: High restart count (restart loop)

- GIVEN a service with a restart count of 5 or more
- WHEN displayed in the ServicePanel
- THEN it shows the restart indicator (e.g., "↻12") next to the status
- AND the indicator is styled in red to signal a critical problem

### Requirement: Restart Count Reset

The restart count display MUST reflect the current Docker state.

#### Scenario: Count resets after manual restart

- GIVEN a service showing "↻5" from previous crash loops
- WHEN the user manually restarts the service via the dashboard
- THEN the container is recreated by Docker
- AND the restart count returns to 0 on the next refresh
- AND the restart indicator disappears

#### Scenario: Count updates on refresh

- GIVEN the dashboard refresh timer fires every 10 seconds
- WHEN `_refresh_status()` runs
- THEN each service's restart count is re-queried
- AND the ServicePanel updates the indicators accordingly

### Requirement: Restart Loop Detection

The system SHOULD help identify actively restart-looping services.

#### Scenario: Auto-select restart-looping service

- GIVEN a service with a restart count of 5 or more
- WHEN the status refresh detects this condition
- THEN the service's checkbox is automatically checked
- AND the service is treated similarly to an unhealthy service for selection purposes
