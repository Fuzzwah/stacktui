## Context

`dashboard.toml` serves as the project-level configuration file. It's intended to be committed to a project's repo so all team members share the same setup. Currently, `save_theme()` writes theme changes directly back to `dashboard.toml`, which makes the file dirty in git — particularly problematic on production where it drifts from the repo.

The `DashboardConfig` dataclass loads config via `tomllib` and writes back via `tomlkit` (format-preserving). The config file is located by `find_config()` which searches CWD then the package directory.

## Goals / Non-Goals

**Goals:**
- Theme cycling (Shift+T) never modifies `dashboard.toml`
- Per-user preferences stored in a separate `.stacktui-user.toml` file alongside the project config
- User prefs file auto-created on first theme save (zero setup)
- `dashboard.toml` `[theme]` becomes the project default, overridden by user prefs
- Structure supports future per-user preferences

**Non-Goals:**
- Global (cross-project) user preferences file
- Migration of existing `[theme]` entries from `dashboard.toml` to user file
- UI for editing preferences beyond theme cycling

## Decisions

### File location: alongside `dashboard.toml` (not XDG/home)

Place `.stacktui-user.toml` in the same directory as `dashboard.toml`.

**Rationale**: Users may prefer different themes per project. Co-locating with the project config means `find_config()` path resolution works unchanged — `user_prefs_path` is simply `config_path.parent / ".stacktui-user.toml"`. Mirrors how `.env` works alongside committed config.

**Alternative considered**: `~/.config/stacktui/preferences.toml` — simpler (one file globally) but prevents per-project preferences and introduces platform-specific path logic.

### Explicit overlay, not generic deep-merge

Each user preference is loaded with an explicit overlay block in `load()`:

```python
user_theme = user_data.get("theme", {}).get("name", "")
if user_theme:
    config.theme_name = user_theme
```

**Rationale**: Easy to reason about, easy to add new prefs (one block each). A generic deep-merge would silently let user files override any project setting, which is not desirable — only specific preferences should be user-overridable.

### Always compute `user_prefs_path` even if file doesn't exist

`load()` sets `user_prefs_path` regardless of whether the file exists. `save_theme()` uses this path to create the file on first write.

**Rationale**: Avoids needing a separate "init" step. The file materializes naturally when the user first cycles themes.

## Risks / Trade-offs

- [User prefs file not gitignored in downstream projects] → Document in `dashboard.toml.example` that `.stacktui-user.toml` should be gitignored. Add to StackTUI's own `.gitignore` as reference.
- [Stale user prefs reference a removed theme] → Existing validation in `on_mount()` already handles this (falls back to Textual default if theme name is invalid).
