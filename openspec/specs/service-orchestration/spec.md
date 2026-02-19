# Service Orchestration Specification

## Purpose

Stop, start, and restart Docker Compose services with smart ordering and build behavior. All orchestration runs in threaded workers with streaming output to both the RichLog widget and an orchestration log file.

## Requirements

### Requirement: Service Selection

Users MUST be able to select services via checkboxes before performing actions.

#### Scenario: Checkbox-based selection

- GIVEN the ServicePanel with checkboxes for each configured service
- WHEN the user checks one or more services
- THEN the visible action buttons update based on the aggregate state of selected services

#### Scenario: Select All

- GIVEN the "Select All" checkbox in the selection controls row below the service list
- WHEN it is toggled on
- THEN all service checkboxes are checked
- AND action buttons update based on aggregate service state

#### Scenario: Auto-switch log on selection

- GIVEN a service checkbox is checked
- WHEN the checkbox value changes to true
- THEN the log viewer dropdown switches to that service (if available)

### Requirement: Stop Action

The system MUST stop all selected services in a single Docker Compose command.

#### Scenario: Stop selected services

- GIVEN services "webapp" and "worker" are checked
- WHEN the user presses Stop (or key `s`)
- THEN `docker compose stop webapp worker` is executed
- AND output streams to the orchestration log and RichLog

### Requirement: Start Action

The system MUST start services with infrastructure-first ordering.

#### Scenario: Start with dependency ordering

- GIVEN infra services "db", "redis" and primary service "webapp" are checked
- WHEN the user presses Start (or key `t`)
- THEN `docker compose up -d db redis` runs first
- AND then `docker compose up -d webapp` runs after
- AND output streams throughout

### Requirement: Restart Action

The system MUST restart infra services with plain restart and rebuild app services.

#### Scenario: Restart mixed services

- GIVEN infra service "redis" and primary service "webapp" are checked
- WHEN the user presses Restart (or key `p`)
- THEN `docker compose restart redis` runs first (no rebuild)
- AND then `docker compose up -d --build webapp` runs after (with rebuild)

### Requirement: Streaming Output

All orchestration commands MUST stream their output in real-time.

#### Scenario: Streaming to dual outputs

- GIVEN an orchestration command is running
- WHEN stdout lines are produced
- THEN each line is written to both the RichLog widget and `logs/orchestration.log`
- AND the orchestration log file is flushed after each line

#### Scenario: Automatic log view switch

- GIVEN an orchestration action starts
- WHEN the action begins
- THEN the log dropdown switches to "Orchestration"
- AND the current log tail is cancelled
- AND the `_orch_in_progress` flag prevents switching away

### Requirement: Exclusive Operation

Only one orchestration action MUST run at a time.

#### Scenario: Concurrent prevention

- GIVEN an orchestration action is running
- WHEN `@work(exclusive=True)` is configured
- THEN a second action invocation replaces the first worker

#### Scenario: Button disabling

- GIVEN an orchestration action starts
- WHEN the action begins
- THEN Stop, Start, and Restart buttons are disabled
- AND they are re-enabled when the action completes (including on error)

### Requirement: Post-Action Refresh

After any orchestration action completes, the system MUST refresh status.

#### Scenario: Status refresh after action

- GIVEN an orchestration action has completed
- WHEN the finally block executes
- THEN `_refresh_status()` is called to update the ServicePanel
