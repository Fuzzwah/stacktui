## 1. DashboardConfig Changes

- [x] 1.1 Add `USER_PREFS_FILENAME = ".stacktui-user.toml"` constant near `PROJECT_ROOT` in `stacktui/dashboard.py`
- [x] 1.2 Add `user_prefs_path: Path | None = None` field to `DashboardConfig` after `config_path`
- [x] 1.3 Extend `DashboardConfig.load()` to compute `user_prefs_path` from `config_path.parent / USER_PREFS_FILENAME`
- [x] 1.4 Extend `DashboardConfig.load()` to overlay `[theme].name` from `.stacktui-user.toml` if the file exists
- [x] 1.5 Rewrite `save_theme()` to write to `user_prefs_path` instead of `config_path`, auto-creating the file with a comment header if it doesn't exist

## 2. Project Files

- [x] 2.1 Add `.stacktui-user.toml` to `.gitignore`
- [x] 2.2 Update `[theme]` section comments in `dashboard.toml.example` to document project-default vs user-override behavior

## 3. Verification

- [x] 3.1 Run the app and confirm theme loads from `dashboard.toml` when no user prefs file exists
- [x] 3.2 Cycle theme with Shift+T and confirm `.stacktui-user.toml` is created with the new theme
- [x] 3.3 Restart the app and confirm theme loads from `.stacktui-user.toml` (overriding `dashboard.toml`)
- [x] 3.4 Delete `.stacktui-user.toml` and confirm fallback to `dashboard.toml` theme
- [x] 3.5 Confirm `dashboard.toml` is never modified by theme cycling
