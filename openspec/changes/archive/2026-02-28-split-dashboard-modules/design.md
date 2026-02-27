## Context

`stacktui/dashboard.py` is a 2100-line monolith. It contains configuration loading, subprocess helpers, git/docker integration, Textual widgets, the main App class, self-update logic, and the CLI entry point — all in one file. The codebase has grown through incremental feature additions and is now at a size where splitting into modules will improve navigability.

## Goals / Non-Goals

**Goals:**
- Split `dashboard.py` into focused modules with a clean, acyclic import graph
- Preserve all existing behavior — zero functional changes
- Maintain backward compatibility for `from stacktui.dashboard import ...`
- Keep the public API (`Dashboard`, `DashboardConfig`, `main`) unchanged

**Non-Goals:**
- Refactoring logic, renaming functions, or changing APIs
- Splitting the `Dashboard` class itself into mixins (it's ~1000 lines but cohesive)
- Adding tests (separate effort)

## Decisions

### 1. Five modules plus a re-export shim

Split into `config.py`, `helpers.py`, `widgets.py`, `app.py`, `cli.py`. Keep `dashboard.py` as a thin re-export shim.

**Rationale**: These follow the natural dependency layers in the code. The alternatives were: (a) fewer modules (e.g., merging helpers+config) which doesn't reduce the largest file enough, or (b) more modules (e.g., separate `git.py`, `docker.py`, `services.py`) which over-fragments — most helper functions are small and share `_run()` + `DashboardConfig`.

### 2. `find_config()` lives in `helpers.py`, not `config.py`

`find_config()` calls `_run()` and `_detect_compose_project_name()`. Placing it in `config.py` would create a circular dependency (config → helpers → config). Moving it to `helpers.py` keeps the import graph acyclic.

**Alternative considered**: Late imports inside `find_config()`. Rejected as unnecessary complexity when simply placing the function in `helpers.py` works cleanly.

### 3. `WEBHOOK_SIGNAL_FILE` mutable global stays in `helpers.py`

This module-level `Path` is set from `main()` and read by `check_webhook_signal()` and `Dashboard._do_git_pull()`. It must be mutated via `helpers.WEBHOOK_SIGNAL_FILE = ...` (module attribute assignment), not imported with `from .helpers import WEBHOOK_SIGNAL_FILE` which creates a local binding.

### 4. Self-update utilities stay in `helpers.py`

`_is_installed_package()`, `_get_stacktui_repo_root()`, `_check_stacktui_updates()`, `_get_script_relative_path()` are called from both `Dashboard` methods and `cli.py`. Placing them in `cli.py` would create a circular dependency. Keeping them in `helpers.py` avoids this.

### 5. Backward-compat shim in `dashboard.py`

`scripts/take_screenshots.py` does `from stacktui.dashboard import Dashboard, find_config`. The `pyproject.toml` entry point also references `stacktui.dashboard:main`. A re-export shim preserves both without requiring changes to consumers.

## Module Import Graph

```
config.py       ← no internal imports (leaf)
    ↑
helpers.py      ← imports config
    ↑
widgets.py      ← imports config, helpers
    ↑
app.py          ← imports config, helpers, widgets
    ↑
cli.py          ← imports config, helpers, app
```

Strictly acyclic. Each module only imports from modules below it.

## Approximate Sizes

| Module | Lines | Contents |
|--------|-------|----------|
| `config.py` | ~200 | `PROJECT_ROOT`, `DashboardConfig` dataclass |
| `helpers.py` | ~530 | `_run()`, git/docker/service helpers, `ServiceInfo`, `find_config()` |
| `widgets.py` | ~250 | `UpdateBanner`, `WebhookBanner`, `ServicePanel`, `LinksPanel` |
| `app.py` | ~1000 | `Dashboard(App)` class |
| `cli.py` | ~80 | `_self_update()`, `main()` |
| `dashboard.py` | ~20 | Re-export shim |

## Risks / Trade-offs

- **Risk**: `WEBHOOK_SIGNAL_FILE` mutation via module attribute — if someone uses `from .helpers import WEBHOOK_SIGNAL_FILE`, they get a stale reference → **Mitigation**: Use `import stacktui.helpers as helpers; helpers.WEBHOOK_SIGNAL_FILE = ...` pattern in `cli.py`
- **Risk**: `app.py` is still ~1000 lines → **Accepted**: It's a single cohesive class; splitting into mixins adds coupling without meaningful benefit
- **Trade-off**: Backward-compat shim adds a file that just re-exports → **Accepted**: Low maintenance cost, avoids breaking external consumers
