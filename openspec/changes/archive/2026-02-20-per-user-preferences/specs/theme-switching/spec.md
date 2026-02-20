## MODIFIED Requirements

### Requirement: Persist theme on cycle

The dashboard SHALL save the selected theme to `.stacktui-user.toml` (per-user preferences file) whenever the user cycles themes. The project config file (`dashboard.toml`) SHALL NOT be modified.

#### Scenario: Theme saved to user prefs file

- **WHEN** the user presses `Shift+T` to cycle themes
- **THEN** the new theme name is written to the `[theme]` section in `.stacktui-user.toml`
- **AND** `dashboard.toml` is NOT modified
- **AND** the theme persists across application restarts

#### Scenario: User prefs file created if absent

- **WHEN** the user cycles themes
- **AND** `.stacktui-user.toml` does not exist
- **THEN** the file is created with a `[theme]` section containing `name = "<selected>"`

#### Scenario: User prefs theme section updated if present

- **WHEN** the user cycles themes
- **AND** `.stacktui-user.toml` already has `[theme]` with `name = "old-theme"`
- **THEN** the `name` value is updated in place to the new theme

### Requirement: Default theme from configuration

The dashboard SHALL apply a theme on startup by checking the per-user preferences file first, then falling back to the project config, then to the built-in default (`nord`).

#### Scenario: Theme from user prefs

- **WHEN** `.stacktui-user.toml` contains `[theme]` with `name = "gruvbox"`
- **AND** `dashboard.toml` contains `[theme]` with `name = "nord"`
- **THEN** the dashboard starts with the `gruvbox` theme applied

#### Scenario: Theme from project config

- **WHEN** `.stacktui-user.toml` does not exist
- **AND** `dashboard.toml` contains `[theme]` with `name = "textual-dark"`
- **THEN** the dashboard starts with the `textual-dark` theme applied

#### Scenario: No theme configured

- **WHEN** neither `.stacktui-user.toml` nor `dashboard.toml` has a `[theme]` section
- **THEN** the `nord` theme is used as the default

#### Scenario: Invalid theme name configured

- **WHEN** the resolved theme name does not match any available Textual theme
- **THEN** Textual's default theme is used (no crash or error)
