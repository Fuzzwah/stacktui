## 1. Config Layer

- [x] 1.1 Add `last_selected_log: str = ""` field to `DashboardConfig` dataclass
- [x] 1.2 Load `[logs].selected` from `.stacktui-user.toml` in `load_config()` (alongside existing theme loading)
- [x] 1.3 Add `save_selected_log(service: str)` method to `DashboardConfig` mirroring `save_theme()` pattern

## 2. UI Integration

- [x] 2.1 Update `_default_log_service()` to check `config.last_selected_log` against current options before falling back to existing default logic
- [x] 2.2 Call `save_selected_log()` from `on_service_changed()` when the user changes the dropdown selection

## 3. Verification

- [x] 3.1 Run app, change log selection, quit and relaunch — verify saved log is restored
- [x] 3.2 Verify fallback works when saved log source is unavailable (stop the container, relaunch)
- [x] 3.3 Verify `.stacktui-user.toml` contains `[logs]` section with correct `selected` value
