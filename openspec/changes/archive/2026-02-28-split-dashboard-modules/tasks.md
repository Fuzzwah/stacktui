## 1. Create Leaf Module — config.py

- [x] 1.1 Create `stacktui/config.py` with `PROJECT_ROOT`, `USER_PREFS_FILENAME`, and the `DashboardConfig` dataclass (lines 44-245 of dashboard.py)

## 2. Create Helpers Module — helpers.py

- [x] 2.1 Create `stacktui/helpers.py` with `_run()`, `_detect_compose_project_name()`, and `find_config()`
- [x] 2.2 Move git helpers: `get_changed_files()`, `detect_affected_services()`, `get_git_info()`, `get_git_status_summary()`, `get_current_ref()`, `get_git_refs()`
- [x] 2.3 Move docker/compose helpers: `detect_prod_mode()`, `get_compose_file()`, `get_compose_cmd()`, `get_base_url()`
- [x] 2.4 Move `ServiceInfo` class, `_parse_uptime()`, `format_uptime()`
- [x] 2.5 Move service queries: `parse_services()`, `parse_all_containers()`, `detect_native_processes()`
- [x] 2.6 Move `get_data_freshness()`, `get_error_counts()`, `WEBHOOK_SIGNAL_FILE`, `check_webhook_signal()`
- [x] 2.7 Move self-update utilities: `_is_installed_package()`, `_get_stacktui_repo_root()`, `_check_stacktui_updates()`, `_get_script_relative_path()`

## 3. Create Widgets Module — widgets.py

- [x] 3.1 Create `stacktui/widgets.py` with `UpdateBanner`, `WebhookBanner`, `ServicePanel`, `LinksPanel`

## 4. Create App Module — app.py

- [x] 4.1 Create `stacktui/app.py` with the `Dashboard(App)` class (CSS, bindings, all methods)

## 5. Create CLI Module — cli.py

- [x] 5.1 Create `stacktui/cli.py` with `_self_update()` and `main()`, using `helpers.WEBHOOK_SIGNAL_FILE = ...` for the mutable global

## 6. Replace dashboard.py and Update Package Config

- [x] 6.1 Replace `stacktui/dashboard.py` with backward-compat re-export shim
- [x] 6.2 Update `stacktui/__init__.py` to import from new modules
- [x] 6.3 Update `pyproject.toml` entry point to `stacktui.cli:main`

## 7. Update Documentation

- [x] 7.1 Update `CLAUDE.md` project structure and architecture sections

## 8. Verification

- [x] 8.1 Verify `python -c "from stacktui import Dashboard, DashboardConfig, main"` works
- [x] 8.2 Verify `python -c "from stacktui.dashboard import Dashboard, find_config"` works (shim)
- [x] 8.3 Verify app instantiation and all module imports work correctly
