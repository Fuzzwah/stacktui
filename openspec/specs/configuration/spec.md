# Configuration Specification

## Purpose

Manages project configuration loading from TOML files. The `DashboardConfig` dataclass holds all settings and provides service topology properties used throughout the application.

## Requirements

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

### Requirement: Theme write-back
The configuration MUST support saving the theme name back to the source TOML file using `tomlkit` for format-preserving TOML manipulation.

#### Scenario: Save theme to existing theme section
- GIVEN `dashboard.toml` contains `[theme]` with `name = "old"`
- WHEN `DashboardConfig.save_theme("new-theme")` is called
- THEN the `name` value under `[theme]` is updated to `"new-theme"` in the file
- AND all other config content, comments, and formatting are preserved
- AND the file contains valid TOML (no escaped quotes)

#### Scenario: Save theme when no theme section exists
- GIVEN `dashboard.toml` has no `[theme]` section
- WHEN `DashboardConfig.save_theme("nord")` is called
- THEN a `[theme]` section with `name = "nord"` is appended to the file
- AND the file contains valid TOML

#### Scenario: No config path available
- GIVEN `DashboardConfig.config_path` is `None`
- WHEN `save_theme()` is called
- THEN the save is silently skipped (no crash)

#### Scenario: Round-trip preserves file structure

- WHEN `save_theme()` writes the config file
- THEN comments, blank lines, and key ordering in the original file MUST be preserved

### Requirement: Service Topology

The configuration MUST define two categories of services: primary (app) and infrastructure.

#### Scenario: Service ordering

- GIVEN primary services `["webapp", "worker"]` and infra services `["db", "redis"]`
- WHEN `service_order` is accessed
- THEN it returns `["webapp", "worker", "db", "redis"]` (primary first, then infra)

#### Scenario: Service label resolution

- GIVEN a `[services.labels]` mapping of `webapp = "Web App"`
- WHEN a service display name is needed
- THEN the label "Web App" is used instead of the raw service name "webapp"

### Requirement: Path-to-Service Mapping

The configuration MUST support mapping file path prefixes to services via `[[path_map]]` entries.

#### Scenario: Wildcard service mapping

- GIVEN a path_map entry with `service = "*"`
- WHEN a changed file matches that prefix
- THEN all services are considered affected

#### Scenario: Specific service mapping

- GIVEN a path_map entry with `prefix = "app/"` and `service = "webapp"`
- WHEN a changed file starts with "app/"
- THEN only the "webapp" service is considered affected

### Requirement: URL Templating

The configuration MUST support `{base_url}` placeholder in link URLs.

#### Scenario: Dev mode base URL

- GIVEN `urls.dev = "http://localhost:8000"` and a link template `"{base_url}/admin/"`
- WHEN the dashboard is in dev mode
- THEN the link resolves to `"http://localhost:8000/admin/"`

### Requirement: Dev-Only Links

The configuration MUST support links that only appear in development mode via `[links.dev_only]`.

#### Scenario: Dev-only link visibility

- GIVEN a link defined under `[links.dev_only]`
- WHEN the dashboard is in dev mode
- THEN the link is displayed
- AND it is hidden in prod mode

### Requirement: Native Process Detection

The configuration MUST support defining native process patterns via `[native_processes]`.

#### Scenario: Native process config

- GIVEN `[native_processes]` with `bot = "discord_bot/bot.py"`
- WHEN native process detection runs in dev mode
- THEN `pgrep -f "discord_bot/bot.py"` is used to detect the process
