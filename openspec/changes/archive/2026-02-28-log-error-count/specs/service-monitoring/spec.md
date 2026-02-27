## MODIFIED Requirements

### Requirement: Health Status Display

Each service MUST display a colored status indicator with optional uptime and error badge.

#### Scenario: Healthy service

- GIVEN a service with health status "healthy"
- WHEN displayed in the ServicePanel
- THEN it shows a green dot with text "healthy"
- AND appends the uptime in dim style if available
- AND appends an error count badge if the service has errors in recent logs

#### Scenario: Running without healthcheck

- GIVEN a service in "running" state with no health status
- WHEN displayed in the ServicePanel
- THEN it shows a yellow dot with text "running"
- AND appends the uptime in dim style if available
- AND appends an error count badge if the service has errors in recent logs

#### Scenario: Stopped service

- GIVEN a service not found in Docker output
- WHEN displayed in the ServicePanel
- THEN it shows a dim dash "—"
- AND no uptime is displayed
- AND no error badge is displayed
