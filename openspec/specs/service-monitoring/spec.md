# Service Monitoring Specification

## Purpose

Real-time monitoring of Docker Compose service health and status, displayed as colored indicators in the ServicePanel widget. Includes healthcheck freshness tracking and native process detection.

## Requirements

### Requirement: Docker Compose Service Parsing

The system MUST query Docker Compose for service status using JSON output format.

#### Scenario: Parse running services

- GIVEN a Docker Compose project with services running
- WHEN `parse_services()` is called
- THEN it runs `docker compose ps --format json -a`
- AND parses each JSON line into a `ServiceInfo` object
- AND deduplicates by service name, keeping the highest-priority state

#### Scenario: State priority for duplicates

- GIVEN multiple containers for the same service (e.g. during rolling updates)
- WHEN parsing service status
- THEN the container with the highest state priority wins (running > restarting > created > exited/dead)

### Requirement: Cross-Compose Container Discovery

The system MUST discover containers across compose files using `docker ps` directly.

#### Scenario: Container name parsing

- GIVEN containers named `{project}-{service}-{replica}`
- WHEN `parse_all_containers()` is called
- THEN it strips the project prefix and `-1` suffix to derive the service name
- AND extracts health status from the Status string ("(healthy)", "(unhealthy)", "(health: starting)")

### Requirement: Health Status Display

Each service MUST display a colored status indicator.

#### Scenario: Healthy service

- GIVEN a service with health status "healthy"
- WHEN displayed in the ServicePanel
- THEN it shows a green dot with text "healthy"

#### Scenario: Running without healthcheck

- GIVEN a service in "running" state with no health status
- WHEN displayed in the ServicePanel
- THEN it shows a yellow dot with text "running"

#### Scenario: Stopped service

- GIVEN a service not found in Docker output
- WHEN displayed in the ServicePanel
- THEN it shows a dim dash "—"

#### Scenario: Unhealthy service auto-selection

- GIVEN a service that transitions to an unhealthy/stopped state
- WHEN the status refresh detects this change
- THEN the service's checkbox is automatically checked

### Requirement: Automatic Status Refresh

The system MUST refresh service status periodically.

#### Scenario: Refresh interval

- GIVEN the dashboard is mounted
- WHEN the refresh timer fires
- THEN `_refresh_status()` runs every 10 seconds
- AND updates the ServicePanel with current Docker state
- AND checks for webhook signals

### Requirement: Healthcheck Freshness

The system MUST display time since the last successful healthcheck for a configured container.

#### Scenario: Freshness display

- GIVEN `freshness.container = "myproject-webapp-1"` and the container has a passing healthcheck
- WHEN freshness is queried
- THEN it shows "Xm XXs ago" based on the healthcheck log's End timestamp

#### Scenario: No healthcheck configured

- GIVEN `freshness.container` is empty
- WHEN freshness is queried
- THEN it displays "n/a"

### Requirement: Native Process Detection

In dev mode, the system MUST detect services running as native Python processes.

#### Scenario: Native process found

- GIVEN `native_processes` config with `worker = "worker/main.py"`
- WHEN `pgrep -f "worker/main.py"` returns a PID
- THEN a `ServiceInfo` with state "running" is added to the service list
- AND it does not duplicate an existing Docker service with the same display name

### Requirement: Queryable Service Health State

The ServicePanel MUST expose per-service health state for external components to query.

#### Scenario: Service statuses stored

- **WHEN** `update_services()` processes service status
- **THEN** a `_service_statuses` dict maps each service name to its current status text

#### Scenario: Get unhealthy services

- **WHEN** `get_unhealthy_services()` is called
- **THEN** it returns the set of service names whose status is not "healthy" and not "running"

#### Scenario: Services with no Docker status

- **WHEN** a configured service has no matching Docker container
- **THEN** it is included in the unhealthy set (status is empty/stopped)
