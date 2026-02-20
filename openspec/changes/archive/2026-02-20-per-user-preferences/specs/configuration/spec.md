## MODIFIED Requirements

### Requirement: TOML Configuration Loading

The system MUST load configuration from a `dashboard.toml` file using Python's stdlib `tomllib`. The loaded config MUST track its source file path for write-back operations. After loading project config, the system MUST check for a per-user preferences file (`.stacktui-user.toml`) in the same directory and overlay any user-specific settings.

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
- AND `DashboardConfig.user_prefs_path` contains the `Path` to `.stacktui-user.toml` in the same directory

#### Scenario: Theme configuration loading with user override

- GIVEN `dashboard.toml` contains `[theme]` with `name = "nord"`
- AND `.stacktui-user.toml` contains `[theme]` with `name = "gruvbox"`
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `"gruvbox"` (user prefs override project default)

#### Scenario: Theme configuration loading without user override

- GIVEN `dashboard.toml` contains `[theme]` with `name = "nord"`
- AND `.stacktui-user.toml` does not exist
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `"nord"` (project default)

#### Scenario: Theme configuration absent

- GIVEN `dashboard.toml` has no `[theme]` section
- AND `.stacktui-user.toml` does not exist
- WHEN the configuration is loaded
- THEN `DashboardConfig.theme_name` is set to `"nord"` (the default)

### Requirement: Theme write-back

The configuration MUST support saving the theme name to the per-user preferences file (`.stacktui-user.toml`) using `tomlkit` for format-preserving TOML manipulation. The project config file (`dashboard.toml`) SHALL NOT be modified by theme save operations.

#### Scenario: Save theme to user prefs file

- GIVEN `.stacktui-user.toml` exists with `[theme]` and `name = "old"`
- WHEN `DashboardConfig.save_theme("new-theme")` is called
- THEN the `name` value under `[theme]` in `.stacktui-user.toml` is updated to `"new-theme"`
- AND `dashboard.toml` is NOT modified

#### Scenario: Save theme when user prefs file does not exist

- GIVEN `.stacktui-user.toml` does not exist
- WHEN `DashboardConfig.save_theme("nord")` is called
- THEN `.stacktui-user.toml` is created with a `[theme]` section containing `name = "nord"`
- AND `dashboard.toml` is NOT modified

#### Scenario: Save theme when no theme section in user prefs

- GIVEN `.stacktui-user.toml` exists but has no `[theme]` section
- WHEN `DashboardConfig.save_theme("nord")` is called
- THEN a `[theme]` section with `name = "nord"` is added to `.stacktui-user.toml`

#### Scenario: No user prefs path available

- GIVEN `DashboardConfig.user_prefs_path` is `None`
- WHEN `save_theme()` is called
- THEN the save is silently skipped (no crash)

#### Scenario: Round-trip preserves user prefs file structure

- WHEN `save_theme()` writes the user prefs file
- THEN comments, blank lines, and key ordering in the existing file MUST be preserved
