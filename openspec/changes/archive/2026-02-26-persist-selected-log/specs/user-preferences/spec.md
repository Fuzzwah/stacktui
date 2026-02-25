## ADDED Requirements

### Requirement: Log selection preference in user prefs

The system SHALL support a `[logs]` section with a `selected` key in `.stacktui-user.toml` for persisting the user's last-selected log source.

#### Scenario: Log selection saved on change

- **WHEN** the user changes the log dropdown selection
- **THEN** the system SHALL save the selected value to `[logs].selected` in `.stacktui-user.toml`
- **AND** create the file if it does not exist

#### Scenario: Log selection loaded from user prefs

- **WHEN** `.stacktui-user.toml` contains `[logs]` with `selected = "file:orchestration"`
- **THEN** `DashboardConfig.last_selected_log` SHALL be set to `"file:orchestration"`

#### Scenario: Empty or missing log selection in user prefs

- **WHEN** `.stacktui-user.toml` exists but has no `[logs]` section or `selected` is empty
- **THEN** `DashboardConfig.last_selected_log` SHALL remain empty string
- **AND** the default log service logic SHALL apply
