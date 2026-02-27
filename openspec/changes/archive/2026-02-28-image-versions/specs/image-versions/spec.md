## ADDED Requirements

### Requirement: Image Data Extraction

The system MUST extract the image name and tag for each running container.

#### Scenario: Query image info

- **WHEN** the refresh cycle runs `docker compose ps --format json`
- **THEN** the system extracts the `Image` field from the JSON output
- **AND** stores the image string in the `ServiceInfo` object's `image` field

#### Scenario: Image with explicit tag

- **GIVEN** a container running `postgres:16.2`
- **WHEN** extracting the image tag
- **THEN** the `image_tag` property returns `"16.2"`

#### Scenario: Image with latest tag

- **GIVEN** a container running `redis:latest`
- **WHEN** extracting the image tag
- **THEN** the `image_tag` property returns `"latest"`

#### Scenario: Image with no tag

- **GIVEN** a container running a locally built image with no tag
- **WHEN** extracting the image tag
- **THEN** the `image_tag` property returns an empty string

### Requirement: Display for Infra vs Primary Services

Image versions MUST be most prominent for infrastructure services.

#### Scenario: Infra service image display

- **GIVEN** an infra service running `postgres:16.2`
- **WHEN** displayed in the ServicePanel via `update_services()`
- **THEN** the image tag `:16.2` is appended after the status and uptime text
- **AND** is styled in dim color

#### Scenario: Primary service image display

- **GIVEN** a primary service running a custom-built image with no meaningful tag
- **WHEN** displayed in the ServicePanel
- **THEN** no image tag is shown

#### Scenario: Stopped service

- **GIVEN** a service that is not running
- **WHEN** displayed in the ServicePanel
- **THEN** no image version is shown

### Requirement: Image Name Truncation

Long image names MUST be truncated to show only the tag portion.

#### Scenario: Short image name

- **GIVEN** an image named `redis:7.4`
- **WHEN** formatting for display
- **THEN** it shows `:7.4`

#### Scenario: Long registry image name

- **GIVEN** an image named `registry.example.com/org/postgres:16.2-alpine`
- **WHEN** formatting for display
- **THEN** only the tag portion is shown: `:16.2-alpine`
- **AND** the registry/repository prefix is omitted

### Requirement: Image Version Refresh

Image versions MUST update when containers are recreated.

#### Scenario: Version update after rebuild

- **GIVEN** a service running `postgres:15.0` that is recreated with `postgres:16.2`
- **WHEN** the next refresh cycle runs
- **THEN** the displayed version updates to `:16.2`
