## MODIFIED Requirements

### Requirement: Three-Column Top Pane

The top pane MUST display three columns side by side.

#### Scenario: Column layout

- GIVEN the dashboard is mounted
- WHEN the top pane renders
- THEN the left column (`col-git`) contains: UpdateBanner, WebhookBanner, LinksPanel, ref selector, Git Pull button
- AND the center column (`col-services`) contains: ServicePanel with freshness display above service checkboxes and status indicators, followed by a selection mode dropdown
- AND the right column (`col-actions`) contains: "Actions" title, action buttons (Restart/Stop/Start), Reload Dashboard button
