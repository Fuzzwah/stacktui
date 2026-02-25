## MODIFIED Requirements

### Requirement: Service Dropdown Population

The service dropdown MUST combine multiple log sources.

#### Scenario: Dropdown ordering

- **WHEN** the dropdown options are generated
- **THEN** the order is: orchestration log (if exists) → running containers (sorted by service_order) → log files not already represented by containers

#### Scenario: Default log service with saved preference

- **WHEN** the dashboard has just mounted
- **AND** `DashboardConfig.last_selected_log` is a non-empty string
- **AND** that value exists in the current dropdown options
- **THEN** the system SHALL use the saved value as the initial log service

#### Scenario: Default log service with stale saved preference

- **WHEN** the dashboard has just mounted
- **AND** `DashboardConfig.last_selected_log` is a non-empty string
- **AND** that value does NOT exist in the current dropdown options
- **THEN** the system SHALL fall through to the existing default logic (first primary service)

#### Scenario: Default log service with no saved preference

- **GIVEN** the dashboard has just mounted
- **WHEN** `DashboardConfig.last_selected_log` is empty
- **THEN** it prefers the first primary service found in the dropdown options
