# User Preferences Specification

## Purpose

Provides per-user preference storage that overlays project-level configuration. User preferences live in `.stacktui-user.toml` alongside `dashboard.toml` and are not committed to version control.

## Requirements

### Requirement: Per-user preferences file

The system SHALL support a per-user preferences file (`.stacktui-user.toml`) that lives alongside `dashboard.toml` and overrides specific project-level settings with user-specific values.

#### Scenario: User prefs file location

- **WHEN** `dashboard.toml` is loaded from a directory
- **THEN** the system SHALL look for `.stacktui-user.toml` in the same directory

#### Scenario: User prefs file does not exist

- **WHEN** `.stacktui-user.toml` does not exist
- **THEN** the system SHALL use project defaults from `dashboard.toml` without error

#### Scenario: User prefs file auto-created on first save

- **WHEN** a user preference is saved for the first time
- **AND** `.stacktui-user.toml` does not exist
- **THEN** the system SHALL create the file with a descriptive comment header
- **AND** write the preference value

#### Scenario: User prefs override project defaults

- **WHEN** both `dashboard.toml` and `.stacktui-user.toml` define a value for the same setting
- **THEN** the value from `.stacktui-user.toml` SHALL take precedence

#### Scenario: User prefs path always computed

- **WHEN** a config file is loaded
- **THEN** `DashboardConfig.user_prefs_path` SHALL be set to the expected user prefs file path
- **AND** this path SHALL be set regardless of whether the file currently exists

### Requirement: Theme preference in user prefs

The system SHALL support a `[theme]` section with a `name` key in `.stacktui-user.toml`.

#### Scenario: Theme loaded from user prefs

- **WHEN** `.stacktui-user.toml` contains `[theme]` with `name = "gruvbox"`
- **AND** `dashboard.toml` contains `[theme]` with `name = "nord"`
- **THEN** the dashboard SHALL start with the `gruvbox` theme

#### Scenario: Empty theme in user prefs

- **WHEN** `.stacktui-user.toml` exists but has no `[theme]` section or `name` is empty
- **THEN** the project default from `dashboard.toml` SHALL be used
