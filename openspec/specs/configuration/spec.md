# Configuration Specification

## Purpose

Manages project configuration loading from TOML files. The `DashboardConfig` dataclass holds all settings and provides service topology properties used throughout the application.

## Requirements

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
