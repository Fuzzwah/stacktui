## REMOVED Requirements

### Requirement: Selection Controls Layout
**Reason**: Replaced by the new Selection Dropdown requirement. The horizontal row of checkbox + buttons is removed in favor of a Select widget.
**Migration**: See added requirement "Selection Dropdown" below.

### Requirement: Select All Control
**Reason**: Replaced by the "All" option in the selection dropdown.
**Migration**: Users select "All" from the dropdown instead of toggling a checkbox.

### Requirement: Select Changed Button
**Reason**: Replaced by the "Changed" option in the selection dropdown.
**Migration**: Users select "Changed" from the dropdown. The dropdown is always visible (no conditional show/hide).

### Requirement: Select Unhealthy Button
**Reason**: Replaced by the "Stopped" option in the selection dropdown, which covers unhealthy/stopped services.
**Migration**: Users select "Stopped" from the dropdown.

## ADDED Requirements

### Requirement: Selection Dropdown
The services column MUST contain a Select dropdown below the service list with options: All, Changed, Stopped, Running, None.

#### Scenario: Dropdown rendering
- **WHEN** the services column renders
- **THEN** a Select dropdown with id `selection-mode` appears below the ServicePanel
- **AND** it contains options: ("All", "all"), ("Changed", "changed"), ("Stopped", "stopped"), ("Running", "running"), ("None", "none")
- **AND** its initial value is blank (prompt text visible)

#### Scenario: Select "All"
- **WHEN** the user selects "All" from the dropdown
- **THEN** all service checkboxes are checked
- **AND** the dropdown resets to blank

#### Scenario: Select "Changed"
- **WHEN** the user selects "Changed" from the dropdown
- **AND** `_affected_services` is non-empty
- **THEN** all service checkboxes are unchecked
- **AND** only services in `_affected_services` have their checkboxes checked
- **AND** the dropdown resets to blank

#### Scenario: Select "Changed" with no affected services
- **WHEN** the user selects "Changed" from the dropdown
- **AND** `_affected_services` is empty
- **THEN** all service checkboxes are unchecked
- **AND** the dropdown resets to blank

#### Scenario: Select "Stopped"
- **WHEN** the user selects "Stopped" from the dropdown
- **THEN** all service checkboxes are unchecked
- **AND** only services with status not in ("healthy", "running") have their checkboxes checked
- **AND** the dropdown resets to blank

#### Scenario: Select "Running"
- **WHEN** the user selects "Running" from the dropdown
- **THEN** all service checkboxes are unchecked
- **AND** only services with status "healthy" or "running" have their checkboxes checked
- **AND** the dropdown resets to blank

#### Scenario: Select "None"
- **WHEN** the user selects "None" from the dropdown
- **THEN** all service checkboxes are unchecked
- **AND** the dropdown resets to blank

## MODIFIED Requirements

### Requirement: Affected Service Tracking

The system MUST persist git-pull affected services as application state and auto-select them.

#### Scenario: Git pull detects affected services
- **WHEN** `_do_git_pull()` completes and `detect_affected_services()` returns a non-empty set
- **THEN** the affected services are stored in `self._affected_services`
- **AND** each affected service's checkbox is set to checked

#### Scenario: Affected services cleared after restart
- **WHEN** a restart action completes for services that were in `_affected_services`
- **THEN** those services are removed from `_affected_services`
