## Why

`dashboard.toml` is meant to be committed to a project's repo so all team members share the same project configuration. When a user cycles the theme with Shift+T, `save_theme()` writes back to `dashboard.toml`, making the file dirty in git. On production servers, this puts the user's local config out of sync with the repo. Theme preference is inherently per-user, not per-project.

## What Changes

- Introduce a per-user preferences file (`.stacktui-user.toml`) that lives alongside `dashboard.toml` but is gitignored
- Theme in `dashboard.toml` becomes the **project default**; user prefs file takes precedence
- `save_theme()` writes to the user prefs file instead of `dashboard.toml`
- The user prefs file is auto-created on first theme cycle (no setup required)
- The file structure supports future per-user preferences beyond theme

## Capabilities

### New Capabilities
- `user-preferences`: Per-user preferences file that overlays project config, starting with theme selection

### Modified Capabilities
- `configuration`: Config loading now includes a user preferences overlay step; `save_theme()` targets the user prefs file instead of `dashboard.toml`
- `theme-switching`: Theme persistence now writes to `.stacktui-user.toml` instead of `dashboard.toml`

## Impact

- `stacktui/dashboard.py`: `DashboardConfig` gains a `user_prefs_path` field; `load()` overlays user prefs; `save_theme()` writes to user prefs file
- `.gitignore`: Add `.stacktui-user.toml`
- `dashboard.toml.example`: Updated comments documenting the project-default vs user-override behavior
- No new dependencies (uses existing `tomllib` + `tomlkit`)
