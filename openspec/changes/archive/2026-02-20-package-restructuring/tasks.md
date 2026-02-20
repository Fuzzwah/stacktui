# Package Restructuring — Tasks

## 1. Package Structure

- [x] 1.1 Create `stacktui/` directory
- [x] 1.2 Move `dashboard.py` to `stacktui/dashboard.py`
- [x] 1.3 Create `stacktui/__init__.py` exporting `Dashboard`, `DashboardConfig`, `main`

## 2. Build Configuration

- [x] 2.1 Update `pyproject.toml` entry point from `dashboard:main` to `stacktui.dashboard:main`
- [x] 2.2 Add `[build-system]` section with `hatchling` backend
- [x] 2.3 Bump version from `0.1.0` to `0.2.0`

## 3. Documentation

- [x] 3.1 Update README.md quick start and usage instructions for new package structure
- [x] 3.2 Update CLAUDE.md project structure section

## 4. Verification

- [x] 4.1 Verify `uv sync` installs the package correctly
- [x] 4.2 Verify `uv run stacktui --dev` launches the dashboard
