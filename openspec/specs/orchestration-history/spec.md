# Orchestration History Specification

## Purpose

Display a compact list of recent orchestration actions with timestamps, so users can see what operations were performed and when. Currently, orchestration output is only visible during the active operation and then lost from the UI.

## Requirements

### Requirement: History Data Source

The system MUST derive history from the orchestration log file.

#### Scenario: Parse orchestration log

- GIVEN `logs/orchestration.log` exists with logged operations
- WHEN the orchestration history is built
- THEN the system parses the log file for operation start/end markers
- AND extracts the action type, affected services, and timestamp for each operation

#### Scenario: No orchestration log

- GIVEN no `logs/orchestration.log` exists
- WHEN the orchestration history is queried
- THEN an empty history is displayed
- AND no error is raised

### Requirement: History Entry Format

Each history entry MUST show the action, services, and relative time.

#### Scenario: Recent action display

- GIVEN a restart of webapp and worker that completed 2 hours ago
- WHEN displayed in the history
- THEN it shows a compact entry (e.g., "Restarted webapp, worker — 2h ago")

#### Scenario: Multiple recent actions

- GIVEN three operations in the last 24 hours
- WHEN displayed in the history
- THEN entries are listed in reverse chronological order (most recent first)

#### Scenario: History limit

- GIVEN many operations over time
- WHEN displaying the history
- THEN only the most recent entries are shown (e.g., last 5-10 operations)
- AND older entries are not loaded or displayed

### Requirement: History Display Location

The orchestration history MUST be visible without switching to the log viewer.

#### Scenario: Display in actions panel

- GIVEN recent orchestration history exists
- WHEN the actions panel is rendered
- THEN the history is shown below the action buttons
- AND uses a compact, space-efficient format

#### Scenario: Empty history

- GIVEN no orchestration operations have been performed
- WHEN the actions panel is rendered
- THEN no history section is shown
- AND the panel layout is unchanged

### Requirement: History Updates

The history MUST update after operations complete.

#### Scenario: Update after orchestration

- GIVEN the user restarts services via the dashboard
- WHEN the orchestration completes
- THEN the history list is refreshed
- AND the new operation appears at the top

#### Scenario: Refresh on dashboard load

- GIVEN orchestration operations were performed in a previous session
- WHEN the dashboard starts
- THEN the history is loaded from the orchestration log
- AND recent entries are displayed immediately
