## Context

StackTUI already has a per-user preferences system (`.stacktui-user.toml`) used to persist theme selection via `save_theme()` / `load_config()`. The log dropdown resets to the first primary service on every app launch. Users want the last-selected log source to be remembered across sessions.

## Goals / Non-Goals

**Goals:**
- Persist the user's log dropdown selection to `.stacktui-user.toml`
- Restore it on next launch if the log source is still available
- Follow the exact same pattern as theme persistence

**Non-Goals:**
- Persisting other UI state (scroll position, selected services, etc.)
- Adding a general-purpose preferences API beyond the existing pattern

## Decisions

### Reuse existing `save_theme()` pattern for `save_selected_log()`

**Rationale:** The theme persistence code already handles file creation, tomlkit formatting, and the guard for `user_prefs_path is None`. A parallel `save_selected_log()` method on `DashboardConfig` keeps it consistent.

**Alternative considered:** A generic `save_pref(section, key, value)` method — rejected as over-engineering for two preferences.

### Add `last_selected_log` field to `DashboardConfig`

**Rationale:** Loaded during `load_config()` alongside the theme, stored as a plain string matching the Select widget value (e.g., `"webapp"`, `"file:orchestration"`). Empty string means no saved preference.

### Validate saved selection against current options in `_default_log_service()`

**Rationale:** Log sources are dynamic (containers start/stop, log files appear/disappear). The saved value must be checked against `_get_service_options()` before use. If not found, fall through to existing default logic.

## Risks / Trade-offs

- [Stale saved value] The saved log source may no longer exist → Mitigated by validation against current options with fallback to default logic.
- [Write on every selection change] Disk write on each dropdown change → Acceptable: single small TOML file, infrequent user action, matches theme save behavior.
