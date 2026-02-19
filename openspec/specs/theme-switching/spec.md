# Theme Switching Specification

## Purpose

Allows users to change the dashboard's visual theme at runtime and configure a default theme on startup. Leverages Textual's built-in theme system.

## Requirements

### Requirement: Theme cycling keybinding
The dashboard SHALL provide a `Shift+T` keybinding that cycles through all available Textual themes.

#### Scenario: Cycle to next theme
- **WHEN** the user presses `Shift+T`
- **THEN** the app's theme changes to the next theme in alphabetical order
- **AND** a notification displays the new theme name

#### Scenario: Wrap around at end of theme list
- **WHEN** the current theme is the last in alphabetical order
- **AND** the user presses `Shift+T`
- **THEN** the theme wraps around to the first theme in the list

### Requirement: Default theme from configuration
The dashboard SHALL apply a default theme from the `[theme]` config section on startup.

#### Scenario: Theme configured in TOML
- **WHEN** `dashboard.toml` contains `[theme]` with `name = "nord"`
- **THEN** the dashboard starts with the "nord" theme applied

#### Scenario: No theme configured
- **WHEN** `dashboard.toml` has no `[theme]` section
- **THEN** Textual's default theme (`textual-dark`) is used

#### Scenario: Invalid theme name configured
- **WHEN** `dashboard.toml` contains `[theme]` with `name = "nonexistent"`
- **THEN** Textual's default theme is used (no crash or error)

### Requirement: Command palette theme access
The Textual command palette (`Ctrl+P`) SHALL list all available themes for selection.

#### Scenario: Select theme from command palette
- **WHEN** the user opens the command palette with `Ctrl+P`
- **AND** types a theme name
- **THEN** the matching theme is applied immediately
