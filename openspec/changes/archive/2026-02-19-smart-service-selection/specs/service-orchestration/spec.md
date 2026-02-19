## MODIFIED Requirements

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
