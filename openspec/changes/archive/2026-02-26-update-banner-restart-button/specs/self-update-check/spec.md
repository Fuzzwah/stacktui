## MODIFIED Requirements

### Requirement: Update banner display
The system SHALL display an `UpdateBanner` widget when updates are available, showing the number of commits behind. The banner SHALL contain a "Restart to Update" button that pulls the StackTUI repo and re-execs the process. The banner SHALL be hidden when the local copy is up to date.

#### Scenario: Updates available
- **WHEN** `_check_stacktui_updates()` returns a value greater than 0
- **THEN** the UpdateBanner is visible with text indicating the number of commits behind
- **AND** a "Restart to Update" button is displayed alongside the text

#### Scenario: No updates
- **WHEN** `_check_stacktui_updates()` returns `0`
- **THEN** the UpdateBanner is hidden

#### Scenario: User clicks Restart to Update
- **WHEN** the user presses the "Restart to Update" button
- **THEN** the system runs `git pull --ff-only` in the StackTUI repo directory
- **AND** the process re-execs via `os.execv()` with the same arguments
