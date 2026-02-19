## MODIFIED Requirements

### Requirement: Three-Column Top Pane

The top pane MUST display three columns side by side.

#### Scenario: Column layout

- GIVEN the dashboard is mounted
- WHEN the top pane renders
- THEN the left column (`col-git`) contains: WebhookBanner, LinksPanel, ref selector, Git Pull button
- AND the center column (`col-services`) contains: ServicePanel with checkboxes and status indicators, followed by a horizontal selection controls row (Select All, Changed, Unhealthy)
- AND the right column (`col-actions`) contains: "Actions" title, action buttons (Restart/Stop/Start), Reload Dashboard button

### Requirement: Action Button Visibility

Action buttons MUST appear based on the aggregate state of selected services.

#### Scenario: No services selected

- GIVEN no service checkboxes are checked
- WHEN the checkbox state changes
- THEN all action buttons (Restart, Stop, Start) are hidden

#### Scenario: All selected services healthy or running

- GIVEN all checked services have status "healthy" or "running"
- WHEN the checkbox or status state changes
- THEN only Restart and Stop buttons are visible
- AND Start button is hidden

#### Scenario: All selected services stopped

- GIVEN all checked services have status "stopped", "exited", or no Docker status
- WHEN the checkbox or status state changes
- THEN only Start button is visible
- AND Restart and Stop buttons are hidden

#### Scenario: Mixed service states selected

- GIVEN checked services have a mix of running and stopped states
- WHEN the checkbox or status state changes
- THEN all three buttons (Restart, Stop, Start) are visible
