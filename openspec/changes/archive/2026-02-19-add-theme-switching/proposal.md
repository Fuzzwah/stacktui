## Why

StackTUI has no way to change its visual appearance. Textual ships with multiple built-in themes (nord, gruvbox, tokyo-night, solarized-light, etc.) and a command palette theme picker, but the app doesn't expose any of this. Users should be able to personalize the dashboard and switch between light/dark themes.

## What Changes

- Add a keybinding (`Shift+T`) to cycle through available Textual themes
- Add an optional `[theme]` config section to set a default theme on startup
- Textual's command palette (`Ctrl+P`) will automatically list all themes with no extra code

## Capabilities

### New Capabilities
- `theme-switching`: Keybinding to cycle themes, optional config for default theme, command palette integration

### Modified Capabilities
- `configuration`: Add optional `[theme]` section with `name` key to `DashboardConfig`

## Impact

- **Code**: `dashboard.py` — `DashboardConfig` dataclass, `BINDINGS`, `on_mount()`, new action method
- **Config**: `dashboard.toml.example` — new `[theme]` section
- **Dependencies**: None (Textual's theme system is built-in)
- **Breaking changes**: None
