## MODIFIED Requirements

### Requirement: Three-Column Top Pane

The top pane MUST display three columns side by side.

#### Scenario: Column layout

- GIVEN the dashboard is mounted
- WHEN the top pane renders
- THEN the left column (`col-git`) contains: UpdateBanner, WebhookBanner, LinksPanel, ref selector, Git Pull button
- AND the center column (`col-services`) contains: ServicePanel with freshness display above service checkboxes and status indicators, followed by a selection mode dropdown
- AND the right column (`col-actions`) contains: "Actions" title, action buttons (Restart/Rebuild/Stop/Start), Reload Dashboard button, and OrchestrationHistory widget showing recent operations

#### Scenario: Orchestration history in actions column

- **WHEN** the actions column renders
- **THEN** the OrchestrationHistory widget MUST appear below the action buttons and Reload button
- AND it displays the 5 most recent orchestration operations in reverse chronological order
- AND each entry shows the action type, service names, and relative timestamp (e.g., "Restarted webapp, worker — 2h ago")

#### Scenario: Empty orchestration history

- **WHEN** no orchestration operations have been performed (no log file or no headers found)
- **THEN** the OrchestrationHistory widget MUST be hidden
- AND the actions column layout is unchanged from its current appearance
