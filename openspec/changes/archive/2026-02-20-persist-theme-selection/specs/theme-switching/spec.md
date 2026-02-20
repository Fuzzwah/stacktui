## ADDED Requirements

### Requirement: Persist theme on cycle
The dashboard SHALL save the selected theme to `dashboard.toml` whenever the user cycles themes.

#### Scenario: Theme saved to config file
- **WHEN** the user presses `Shift+T` to cycle themes
- **THEN** the new theme name is written to the `[theme]` section in `dashboard.toml`
- **AND** the theme persists across application restarts

#### Scenario: Theme section created if absent
- **WHEN** the user cycles themes
- **AND** `dashboard.toml` has no `[theme]` section
- **THEN** a `[theme]` section with `name = "<selected>"` is appended to the file

#### Scenario: Theme section updated if present
- **WHEN** the user cycles themes
- **AND** `dashboard.toml` already has `[theme]` with `name = "old-theme"`
- **THEN** the `name` value is updated in place to the new theme

## MODIFIED Requirements

### Requirement: Default theme from configuration
The dashboard SHALL apply a default theme from the `[theme]` config section on startup. If no theme is configured, the default SHALL be `nord`.

#### Scenario: Theme configured in TOML
- **WHEN** `dashboard.toml` contains `[theme]` with `name = "textual-dark"`
- **THEN** the dashboard starts with the "textual-dark" theme applied

#### Scenario: No theme configured
- **WHEN** `dashboard.toml` has no `[theme]` section
- **THEN** the `nord` theme is used as the default

#### Scenario: Invalid theme name configured
- **WHEN** `dashboard.toml` contains `[theme]` with `name = "nonexistent"`
- **THEN** Textual's default theme is used (no crash or error)
