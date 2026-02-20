## MODIFIED Requirements

### Requirement: TOML Configuration Loading

The system MUST load configuration from a `dashboard.toml` file using Python's stdlib `tomllib`. The loaded config MUST track its source file path for write-back operations.

#### Scenario: Config file search order

- GIVEN no `--config` flag is provided
- WHEN the application starts
- THEN it searches for `dashboard.toml` in the current working directory first
- AND falls back to the package's parent directory (i.e., the repository root when installed in development mode)
- AND exits with an error if no config file is found

#### Scenario: Explicit config path

- GIVEN the `--config path/to/file.toml` flag is provided
- WHEN the application starts
- THEN it loads config from exactly that path
- AND exits with an error if the file does not exist

#### Scenario: Config path tracking

- GIVEN a config file is loaded from any source
- WHEN the configuration object is created
- THEN `DashboardConfig.config_path` contains the `Path` to the loaded file

#### Scenario: Theme configuration loading

- GIVEN `dashboard.toml` contains a `[theme]` section with `name = "nord"`
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `"nord"`

#### Scenario: Theme configuration absent

- GIVEN `dashboard.toml` has no `[theme]` section
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `"nord"` (the default)

## ADDED Requirements

### Requirement: Theme write-back
The configuration MUST support saving the theme name back to the source TOML file.

#### Scenario: Save theme to existing theme section
- GIVEN `dashboard.toml` contains `[theme]` with `name = "old"`
- WHEN `DashboardConfig.save_theme("new-theme")` is called
- THEN the `name` value under `[theme]` is updated to `"new-theme"` in the file
- AND all other config content is preserved

#### Scenario: Save theme when no theme section exists
- GIVEN `dashboard.toml` has no `[theme]` section
- WHEN `DashboardConfig.save_theme("nord")` is called
- THEN a `[theme]` section with `name = "nord"` is appended to the file

#### Scenario: No config path available
- GIVEN `DashboardConfig.config_path` is `None`
- WHEN `save_theme()` is called
- THEN the save is silently skipped (no crash)
