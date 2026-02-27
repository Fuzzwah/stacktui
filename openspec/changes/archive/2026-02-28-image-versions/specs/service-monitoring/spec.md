## MODIFIED Requirements

### Requirement: Docker Compose Service Parsing

The system MUST query Docker Compose for service status using JSON output format.

#### Scenario: Parse running services

- GIVEN a Docker Compose project with services running
- WHEN `parse_services()` is called
- THEN it runs `docker compose ps --format json -a`
- AND parses each JSON line into a `ServiceInfo` object
- AND deduplicates by service name, keeping the highest-priority state
- AND extracts the uptime duration from the `Status` field into `ServiceInfo.uptime_seconds`
- AND extracts the image string from the `Image` field into `ServiceInfo.image`

#### Scenario: State priority for duplicates

- GIVEN multiple containers for the same service (e.g. during rolling updates)
- WHEN parsing service status
- THEN the container with the highest state priority wins (running > restarting > created > exited/dead)

### Requirement: Health Status Display

Each service MUST display a colored status indicator with optional uptime and image tag.

#### Scenario: Healthy service

- GIVEN a service with health status "healthy"
- WHEN displayed in the ServicePanel
- THEN it shows a green dot with text "healthy"
- AND appends the uptime in dim style if available
- AND appends the image tag in dim style if the service is an infra service with a non-empty tag

#### Scenario: Running without healthcheck

- GIVEN a service in "running" state with no health status
- WHEN displayed in the ServicePanel
- THEN it shows a yellow dot with text "running"
- AND appends the uptime in dim style if available
- AND appends the image tag in dim style if the service is an infra service with a non-empty tag

#### Scenario: Stopped service

- GIVEN a service not found in Docker output
- WHEN displayed in the ServicePanel
- THEN it shows a dim dash "—"
- AND no uptime is displayed
- AND no image tag is displayed

#### Scenario: Unhealthy service auto-selection

- GIVEN a service that transitions to an unhealthy/stopped state
- WHEN the status refresh detects this change
- THEN the service's checkbox is automatically checked
