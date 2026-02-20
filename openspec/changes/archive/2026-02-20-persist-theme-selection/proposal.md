## Why

Theme selection via `Shift+T` is lost on restart — users must re-select their preferred theme every session. The theme should persist to `dashboard.toml` automatically. Additionally, the default theme should be `nord` instead of Textual's built-in default.

## What Changes

- When the user cycles themes with `Shift+T`, the selected theme is saved back to `dashboard.toml`
- The default theme changes from empty (Textual's `textual-dark`) to `nord`
- The config file path is tracked on `DashboardConfig` so it can be written back to

## Capabilities

### New Capabilities

_(none — this extends existing capabilities)_

### Modified Capabilities

- `theme-switching`: Add requirement for persisting theme selection to config file on change
- `configuration`: Default theme changes from empty string to `"nord"`; config must track its source file path for write-back

## Impact

- `stacktui/dashboard.py`: `DashboardConfig` dataclass, `DashboardConfig.load()`, `find_config()`, `action_next_theme()`, `on_mount()`
- `dashboard.toml`: Will be modified at runtime when user cycles themes
- No new dependencies (uses stdlib `re` for TOML text manipulation since Python has no TOML writer)
