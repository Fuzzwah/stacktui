# TUI Layout Specification

## Purpose

The terminal user interface layout, keyboard bindings, and widget composition for the Dashboard app built on Textual.

## Requirements

### Requirement: Three-Column Top Pane

The top pane MUST display three columns side by side.

#### Scenario: Column layout

- GIVEN the dashboard is mounted
- WHEN the top pane renders
- THEN the left column (`col-git`) contains: WebhookBanner, LinksPanel, ref selector, Git Pull button
- AND the center column (`col-services`) contains: ServicePanel with checkboxes and status indicators, followed by a horizontal selection controls row (Select All, Changed, Unhealthy)
- AND the right column (`col-actions`) contains: "Actions" title, action buttons (Restart/Stop/Start), Reload Dashboard button

### Requirement: Bottom Pane Log Viewer

The bottom pane MUST display a log viewer with a service selector.

#### Scenario: Log viewer layout

- GIVEN the dashboard is mounted
- WHEN the bottom pane renders
- THEN it contains a `Select` dropdown for choosing the log source
- AND a `RichLog` widget with syntax highlighting, markup, word wrap, auto-scroll, and 2000 max lines

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

### Requirement: Reload Button Visibility

The Reload Dashboard button MUST only appear after a self-update is detected.

#### Scenario: Script updated via git pull

- GIVEN `git pull` updated the dashboard script
- WHEN `_show_reload_button()` is called
- THEN the "hidden" class is removed from the Reload button

#### Scenario: Reload action

- GIVEN the user clicks Reload Dashboard
- WHEN the button is pressed
- THEN `os.execv()` re-executes the current Python process with the same arguments

### Requirement: Keyboard Shortcuts

The dashboard MUST provide keyboard shortcuts for common actions.

#### Scenario: Key bindings

- GIVEN the dashboard is focused
- WHEN the user presses a key
- THEN `q` quits, `r` refreshes status, `g` triggers git pull, `s` stops selected, `t` starts selected, `p` restarts selected, `l` focuses the log service selector

### Requirement: Environment Mode Display

The subtitle MUST show the current environment mode and git info.

#### Scenario: Dev mode subtitle

- GIVEN the dashboard is in dev mode with branch "main" at sha "abc1234"
- WHEN the dashboard mounts
- THEN the subtitle reads "dev | main@abc1234"

### Requirement: Production Mode Detection

The system MUST support auto-detecting production mode.

#### Scenario: Auto-detection via container

- GIVEN `prod_detection.container = "myproject-webapp-1"`
- AND that container is running
- WHEN `detect_prod_mode()` is called
- THEN it returns true

#### Scenario: CLI override

- GIVEN the `--prod` flag is passed
- WHEN the dashboard initializes
- THEN production mode is forced regardless of container state

#### Scenario: Dev override

- GIVEN the `--dev` flag is passed
- WHEN the dashboard initializes
- THEN development mode is forced regardless of container state
