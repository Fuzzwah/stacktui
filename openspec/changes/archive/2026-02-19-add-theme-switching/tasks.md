## 1. Configuration

- [x] 1.1 Add `theme_name: str = ""` field to `DashboardConfig` dataclass
- [x] 1.2 Add `[theme]` section parsing in `DashboardConfig.load()` to read `name` key
- [x] 1.3 Add `[theme]` section with `name` key to `dashboard.toml.example` with comment

## 2. Theme Switching

- [x] 2.1 Add `Binding("T", "next_theme", "Theme")` to `Dashboard.BINDINGS`
- [x] 2.2 Implement `action_next_theme()` method: cycle through sorted `self.available_themes`, set `self.theme`, call `self.notify()` with theme name
- [x] 2.3 Apply configured theme in `on_mount()`: set `self.theme = config.theme_name` if non-empty

## 3. Verification

- [ ] 3.1 Run app with demo stack and test `Shift+T` cycles themes with notification
- [ ] 3.2 Test `Ctrl+P` command palette lists themes
- [ ] 3.3 Test `[theme] name = "nord"` in config starts app with Nord theme
- [ ] 3.4 Test missing `[theme]` section defaults to `textual-dark`
