# Image Versions Specification

## Purpose

Display the Docker image tag or version next to infrastructure services (e.g., `postgres:16.2`, `redis:7.4`). Answers the common question "what version are we actually running?" without requiring manual Docker commands.

## Requirements

### Requirement: Image Data Extraction

The system MUST extract the image name and tag for each running container.

#### Scenario: Query image info

- GIVEN running Docker Compose services
- WHEN the refresh cycle runs
- THEN the system extracts the image name and tag from `docker compose ps --format json` or `docker inspect --format '{{.Config.Image}}'`
- AND stores the image information in the `ServiceInfo` object

#### Scenario: Image with explicit tag

- GIVEN a container running `postgres:16.2`
- WHEN extracting image info
- THEN the image tag is "16.2"

#### Scenario: Image with latest tag

- GIVEN a container running `redis:latest`
- WHEN extracting image info
- THEN the image tag is "latest"

#### Scenario: Image with no tag

- GIVEN a container running a locally built image with no tag
- WHEN extracting image info
- THEN the image tag is empty or omitted

### Requirement: Display for Infra vs Primary Services

Image versions SHOULD be most prominent for infrastructure services.

#### Scenario: Infra service image display

- GIVEN an infra service (from `[services].infra` config) running `postgres:16.2`
- WHEN displayed in the ServicePanel
- THEN the image tag `:16.2` is shown after the service label
- AND is styled in a dimmed/muted color

#### Scenario: Primary service image display

- GIVEN a primary service (from `[services].primary` config) running a custom-built image
- WHEN displayed in the ServicePanel
- THEN the image tag is either hidden or shown in a more subdued style
- AND locally-built images without meaningful tags do not add visual noise

#### Scenario: Stopped service

- GIVEN a service that is not running
- WHEN displayed in the ServicePanel
- THEN no image version is shown

### Requirement: Image Name Truncation

Long image names MUST be truncated for display.

#### Scenario: Short image name

- GIVEN an image named `redis:7.4`
- WHEN formatting for display
- THEN it shows the full tag `:7.4`

#### Scenario: Long registry image name

- GIVEN an image named `registry.example.com/org/postgres:16.2-alpine`
- WHEN formatting for display
- THEN only the tag portion is shown (`:16.2-alpine`)
- AND the registry/repository prefix is omitted for compactness

### Requirement: Image Version Refresh

Image versions MUST update when containers are recreated.

#### Scenario: Version update after rebuild

- GIVEN a service running `postgres:15.0` that is recreated with `postgres:16.2`
- WHEN the next refresh cycle runs
- THEN the displayed version updates to `:16.2`
