## Why

`stacktui/dashboard.py` is a 2100-line monolith containing configuration, helpers, widgets, the main app class, and the CLI entry point. Navigating and maintaining a single file of this size is increasingly difficult. Splitting it into focused modules improves discoverability and makes the codebase easier to work with.

## What Changes

- Split `dashboard.py` into 5 focused modules: `config.py`, `helpers.py`, `widgets.py`, `app.py`, `cli.py`
- Replace `dashboard.py` with a thin re-export shim for backward compatibility
- Update `__init__.py` to import from new module locations
- Update `pyproject.toml` entry point to `stacktui.cli:main`
- Update `CLAUDE.md` to reflect the new project structure

## Capabilities

### New Capabilities

_(none — this is a pure internal refactor with no new user-facing capabilities)_

### Modified Capabilities

_(none — all existing behavior is preserved unchanged; only the internal file organization changes)_

## Impact

- **Code**: Every symbol currently in `dashboard.py` moves to one of the new modules
- **Public API**: Unchanged — `__init__.py` continues to export `Dashboard`, `DashboardConfig`, `main`
- **Backward compat**: `from stacktui.dashboard import ...` continues to work via re-export shim
- **Entry point**: `pyproject.toml` script changes from `stacktui.dashboard:main` to `stacktui.cli:main`
- **External consumers**: `scripts/take_screenshots.py` works unchanged via the shim
- **Dependencies**: No new dependencies
