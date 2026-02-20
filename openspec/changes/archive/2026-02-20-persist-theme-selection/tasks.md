## 1. Config Path Tracking

- [x] 1.1 Add `config_path: Path | None = None` field to `DashboardConfig` dataclass
- [x] 1.2 Set `config.config_path = path` in `DashboardConfig.load()` before returning

## 2. Default Theme

- [x] 2.1 Change `theme_name` default from `""` to `"nord"` in `DashboardConfig`
- [x] 2.2 Update `on_mount()` to apply theme unconditionally (remove `if self._config.theme_name:` guard)

## 3. Theme Write-Back

- [x] 3.1 Add `import re` to module imports
- [x] 3.2 Add `save_theme(theme_name: str)` method to `DashboardConfig` — reads TOML file as text, uses regex to update/insert `[theme]` section, writes back
- [x] 3.3 Call `self._config.save_theme(theme_name)` in `action_next_theme()` after setting `self.theme`

## 4. Verification

- [x] 4.1 Run app with no `[theme]` section in config — verify it starts with `nord`
- [x] 4.2 Press `T` to cycle theme — verify `[theme]` section appears in `dashboard.toml`
- [x] 4.3 Restart app — verify the saved theme is applied
