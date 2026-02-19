## ADDED Requirements

### Requirement: Affected Service Tracking

The system MUST persist git-pull affected services as application state and auto-select them.

#### Scenario: Git pull detects affected services

- **WHEN** `_do_git_pull()` completes and `detect_affected_services()` returns a non-empty set
- **THEN** the affected services are stored in `self._affected_services`
- **AND** each affected service's checkbox is set to checked

#### Scenario: Affected services cleared after restart

- **WHEN** a restart action completes for services that were in `_affected_services`
- **THEN** those services are removed from `_affected_services`

### Requirement: Selection Controls Layout

Selection controls MUST appear below the service list in a horizontal row.

#### Scenario: Selection controls rendering

- **WHEN** the services column renders
- **THEN** a horizontal row appears below the ServicePanel
- **AND** it contains: "Select All" checkbox, "Changed" button, "Unhealthy" button

### Requirement: Select All Control

The "Select All" checkbox MUST toggle all service checkboxes.

#### Scenario: Select All toggled on

- **WHEN** the user checks "Select All"
- **THEN** all service checkboxes are checked

#### Scenario: Select All toggled off

- **WHEN** the user unchecks "Select All"
- **THEN** all service checkboxes are unchecked

### Requirement: Select Changed Button

The "Changed" button MUST select services affected by the last git pull.

#### Scenario: Changed button visible

- **WHEN** `_affected_services` is non-empty
- **THEN** the "Changed" button is visible

#### Scenario: Changed button hidden

- **WHEN** `_affected_services` is empty
- **THEN** the "Changed" button is hidden

#### Scenario: Changed button pressed

- **WHEN** the user clicks the "Changed" button
- **THEN** all services in `_affected_services` have their checkboxes checked

### Requirement: Select Unhealthy Button

The "Unhealthy" button MUST select services that are unhealthy or stopped.

#### Scenario: Unhealthy button visible

- **WHEN** any services have a status that is not "healthy" or "running"
- **THEN** the "Unhealthy" button is visible

#### Scenario: Unhealthy button hidden

- **WHEN** all services are "healthy" or "running"
- **THEN** the "Unhealthy" button is hidden

#### Scenario: Unhealthy button pressed

- **WHEN** the user clicks the "Unhealthy" button
- **THEN** all unhealthy/stopped services have their checkboxes checked
