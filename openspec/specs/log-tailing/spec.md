# Log Tailing Specification

## Purpose

Real-time log streaming from Docker containers and local log files, displayed in a RichLog widget. Users select the log source from a dropdown that dynamically combines running containers and configured log files.

## Requirements

### Requirement: Docker Container Log Tailing

The system MUST stream logs from Docker Compose services in real-time.

#### Scenario: Tail Docker logs

- GIVEN a running Docker service "webapp"
- WHEN the user selects "webapp" in the service dropdown
- THEN the system runs `docker compose logs -f --tail 200 webapp`
- AND streams stdout line-by-line to the RichLog widget

#### Scenario: Cross-compose-file service detection

- GIVEN a service that exists in a different compose file than the current mode
- WHEN tailing logs for that service
- THEN `_compose_file_for_service()` checks both dev and prod compose files
- AND uses whichever one manages the service

### Requirement: File Log Tailing

The system MUST support tailing local log files.

#### Scenario: Tail a named log file

- GIVEN a log file configured as `worker = "worker.log"` under `[logs.files]`
- WHEN the user selects "worker (log file)" in the dropdown
- THEN the system reads the last 200 lines of the file
- AND then polls for new lines every 0.5 seconds

#### Scenario: Orchestration log

- GIVEN an orchestration action has created `logs/orchestration.log`
- WHEN the user views the dropdown
- THEN "Orchestration" appears as the first option (if the file exists)

#### Scenario: Missing log file

- GIVEN a configured log file that does not exist on disk
- WHEN the user selects it
- THEN the RichLog displays "Log file not found: {name}"
- AND suggests starting the service to create the file

### Requirement: Service Dropdown Population

The service dropdown MUST combine multiple log sources.

#### Scenario: Dropdown ordering

- GIVEN running containers and configured log files
- WHEN the dropdown options are generated
- THEN the order is: orchestration log (if exists) → running containers (sorted by service_order) → log files not already represented by containers

#### Scenario: Default log service

- GIVEN the dashboard has just mounted
- WHEN choosing the initial log service
- THEN it prefers the first primary service found in the dropdown options

### Requirement: Log Source Switching

The system MUST cleanly switch between log sources.

#### Scenario: Switch log source

- WHEN the user changes the service dropdown selection
- THEN the current log task is cancelled
- AND the current log subprocess is terminated
- AND the RichLog is cleared
- AND a new log tailing task starts for the selected source

### Requirement: Orchestration Log Lock

During orchestration actions, the log view MUST be locked to the orchestration log.

#### Scenario: Orchestration in progress

- GIVEN an orchestration action (stop/start/restart/git pull) is running
- WHEN the user tries to switch log source
- THEN `_start_log_tail()` returns early without switching
- AND the orchestration output continues streaming
