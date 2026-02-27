# Port Mappings Specification

## Purpose

Display exposed port mappings next to each service in the ServicePanel (e.g., `:8000`, `:5432`). Eliminates the need to mentally track or look up which port each service is available on.

## Requirements

### Requirement: Port Data Extraction

The system MUST extract published port mappings from Docker Compose output.

#### Scenario: Parse port mappings from docker compose ps

- **WHEN** `parse_services()` processes the `docker compose ps --format json` output
- **THEN** it extracts the `Publishers` array from each JSON object
- AND filters to entries where `PublishedPort` > 0
- AND stores the sorted, deduplicated list of `PublishedPort` values in the `ServiceInfo.ports` field

#### Scenario: Service with no published ports

- **WHEN** parsing a service with no `Publishers` array or all `PublishedPort` values are 0
- **THEN** the `ServiceInfo.ports` list is empty

### Requirement: Port Display Format

The system MUST display ports in a compact, readable format.

#### Scenario: Single port mapping

- **WHEN** a service has `ports = [8000]`
- **THEN** it displays `:8000` in dimmed style in the ServicePanel status line

#### Scenario: Multiple port mappings

- **WHEN** a service has `ports = [80, 443]`
- **THEN** it displays `:80 :443` with ports separated by a space, in dimmed style

#### Scenario: Host-to-container port mapping

- GIVEN a service mapping host port 3000 to container port 80
- WHEN displayed in the ServicePanel
- THEN it shows `:3000` (the host port, which is what the user connects to)

#### Scenario: No ports to display

- **WHEN** a service has an empty `ports` list
- **THEN** no port information is displayed and no extra whitespace is added

### Requirement: ServicePanel Integration

Port mappings MUST appear inline within each service row.

#### Scenario: Port display position

- **WHEN** a running service has published ports
- **THEN** the port mappings appear after all existing status elements (uptime, image tag, error count)
- AND are styled in dim to match existing metadata styling

#### Scenario: Stopped service ports

- **WHEN** a configured service is not running (no `ServiceInfo` found)
- **THEN** no port information is shown

### Requirement: Port Refresh

Port mappings MUST update when services are restarted with different port configurations.

#### Scenario: Ports update on refresh

- **WHEN** the 10-second refresh timer fires and `_refresh_status()` runs
- **THEN** `parse_services()` re-extracts port data from Docker
- AND the ServicePanel reflects the current port mappings
