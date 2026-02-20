## MODIFIED Requirements

### Requirement: Theme write-back
The configuration MUST support saving the theme name back to the source TOML file using `tomlkit` for format-preserving TOML manipulation.

#### Scenario: Save theme to existing theme section
- **WHEN** `DashboardConfig.save_theme("new-theme")` is called and `dashboard.toml` contains `[theme]` with `name = "old"`
- **THEN** the `name` value under `[theme]` is updated to `"new-theme"` in the file
- AND all other config content, comments, and formatting are preserved
- AND the file contains valid TOML (no escaped quotes)

#### Scenario: Save theme when no theme section exists
- **WHEN** `DashboardConfig.save_theme("nord")` is called and `dashboard.toml` has no `[theme]` section
- **THEN** a `[theme]` section with `name = "nord"` is appended to the file
- AND the file contains valid TOML

#### Scenario: No config path available
- **WHEN** `save_theme()` is called and `DashboardConfig.config_path` is `None`
- **THEN** the save is silently skipped (no crash)

#### Scenario: Round-trip preserves file structure
- **WHEN** `save_theme()` writes the config file
- **THEN** comments, blank lines, and key ordering in the original file MUST be preserved
