## MODIFIED Requirements

### Requirement: TOML Configuration Loading

The system MUST load configuration from a `dashboard.toml` file using Python's stdlib `tomllib`.

#### Scenario: Config file search order

- GIVEN no `--config` flag is provided
- WHEN the application starts
- THEN it searches for `dashboard.toml` in the current working directory first
- AND falls back to the script's parent directory
- AND exits with an error if no config file is found

#### Scenario: Explicit config path

- GIVEN the `--config path/to/file.toml` flag is provided
- WHEN the application starts
- THEN it loads config from exactly that path
- AND exits with an error if the file does not exist

#### Scenario: Theme configuration loading

- GIVEN `dashboard.toml` contains a `[theme]` section with `name = "nord"`
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `"nord"`

#### Scenario: Theme configuration absent

- GIVEN `dashboard.toml` has no `[theme]` section
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `""` (empty string)
