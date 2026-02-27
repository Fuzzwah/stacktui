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

#### Scenario: State priority for duplicates

- GIVEN multiple containers for the same service (e.g. during rolling updates)
- WHEN parsing service status
- THEN the container with the highest state priority wins (running > restarting > created > exited/dead)

### Requirement: Health Status Display

Each service MUST display a colored status indicator with optional uptime.

#### Scenario: Healthy service

- GIVEN a service with health status "healthy"
- WHEN displayed in the ServicePanel
- THEN it shows a green dot with text "healthy"
- AND appends the uptime in dim style if available

#### Scenario: Running without healthcheck

- GIVEN a service in "running" state with no health status
- WHEN displayed in the ServicePanel
- THEN it shows a yellow dot with text "running"
- AND appends the uptime in dim style if available

#### Scenario: Stopped service

- GIVEN a service not found in Docker output
- WHEN displayed in the ServicePanel
- THEN it shows a dim dash "—"
- AND no uptime is displayed
