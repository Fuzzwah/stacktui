# Package Restructuring

## Why

StackTUI was a single-file script (`dashboard.py` at the repo root) with no proper Python package structure. This made it impossible to install as a standard Python package, complicated the entry point configuration in `pyproject.toml`, and didn't follow Python packaging conventions.

## What Changes

- Move `dashboard.py` into a `stacktui/` Python package directory
- Add `stacktui/__init__.py` exporting public API (`Dashboard`, `DashboardConfig`, `main`)
- Update `pyproject.toml` entry point from `dashboard:main` to `stacktui.dashboard:main`
- Add `[build-system]` with `hatchling` backend for standard PEP 517 builds
- Bump version from `0.1.0` to `0.2.0`

## Capabilities

### Modified Capabilities
- `configuration`: `PROJECT_ROOT` now resolves relative to the package directory rather than a standalone script; config search falls back to the package's parent directory

## Impact

- **Code**: `dashboard.py` → `stacktui/dashboard.py`, new `stacktui/__init__.py`
- **Config**: `pyproject.toml` — updated entry point, added build-system, version bump
- **Dependencies**: `hatchling` added as build dependency (build-time only)
- **Breaking changes**: Users who invoked `python dashboard.py` directly must now use `uv run stacktui` or `python -m stacktui.dashboard`
