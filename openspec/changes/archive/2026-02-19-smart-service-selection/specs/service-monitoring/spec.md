## ADDED Requirements

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
