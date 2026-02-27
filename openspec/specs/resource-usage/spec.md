# Resource Usage Specification

## Purpose

Display per-service CPU and memory usage in the ServicePanel, enabling early detection of runaway processes and memory leaks without leaving the dashboard.

## Requirements

### Requirement: Resource Data Collection

The system MUST collect CPU and memory statistics from Docker.

#### Scenario: Query resource stats

- GIVEN running Docker Compose services
- WHEN the refresh cycle runs
- THEN the system runs `docker stats --no-stream --format json` to get a point-in-time snapshot
- AND parses CPU percentage and memory usage for each container

#### Scenario: Single stats call for all containers

- GIVEN multiple running services
- WHEN querying resource stats
- THEN a single `docker stats --no-stream --format json` call returns all containers
- AND the results are matched to services by container name

#### Scenario: Stats call performance

- GIVEN the 10-second refresh interval
- WHEN `docker stats --no-stream` is called
- THEN the call completes within a few seconds
- AND does not block the UI or delay other refresh tasks

### Requirement: Resource Display

Resource usage MUST be shown compactly within each service row.

#### Scenario: CPU and memory display

- GIVEN a service using 45% CPU and 256 MiB memory
- WHEN displayed in the ServicePanel
- THEN it shows a compact representation (e.g., "45% 256M")
- AND the values are styled in a dimmed/muted color

#### Scenario: Low resource usage

- GIVEN a service using 0.1% CPU and 12 MiB memory
- WHEN displayed in the ServicePanel
- THEN it shows "0% 12M" (rounded for compactness)

#### Scenario: High resource usage warning

- GIVEN a service using more than 80% CPU or more than 80% of its memory limit
- WHEN displayed in the ServicePanel
- THEN the resource values are styled in yellow or red to draw attention

#### Scenario: Stopped service

- GIVEN a service that is not running
- WHEN displayed in the ServicePanel
- THEN no resource usage is shown

### Requirement: Memory Format

Memory values MUST be formatted in human-readable units.

#### Scenario: Megabyte range

- GIVEN a container using 384 MiB of memory
- WHEN formatting the value
- THEN it displays "384M"

#### Scenario: Gigabyte range

- GIVEN a container using 2.3 GiB of memory
- WHEN formatting the value
- THEN it displays "2.3G"

### Requirement: Resource Refresh

Resource stats MUST update on each refresh cycle.

#### Scenario: Stats update with service status

- GIVEN the dashboard refresh timer fires
- WHEN `_refresh_status()` runs
- THEN resource stats are collected alongside service status
- AND the ServicePanel updates resource values for all running services

#### Scenario: Graceful degradation

- GIVEN `docker stats` fails or times out
- WHEN the refresh cycle runs
- THEN resource values are cleared or show "—"
- AND the rest of the dashboard continues to function normally
