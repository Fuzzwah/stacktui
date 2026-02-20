# Package Restructuring — Design

## Context

StackTUI was structured as a single `dashboard.py` file at the repository root. While simple, this prevented standard Python packaging (`pip install`, `uv sync` with entry points) and didn't follow conventions expected by build tools.

## Goals / Non-Goals

**Goals:**
- Make StackTUI installable as a standard Python package
- Preserve `PROJECT_ROOT` resolution so config and log paths continue to work
- Add a PEP 517 build backend for compatibility with `pip`, `uv`, and other installers
- Maintain the `stacktui` console entry point

**Non-Goals:**
- Splitting the single-file application into multiple modules (future work)
- Publishing to PyPI (no immediate plan)
- Changing any application behavior or features

## Decisions

### 1. Use a flat package layout (`stacktui/`)

**Rationale:** The simplest standard layout. A single `stacktui/` directory with `__init__.py` and `dashboard.py` keeps the structure minimal while enabling proper imports.

**Alternative considered:** `src/` layout — unnecessary complexity for a single-module package with no namespace conflicts.

### 2. Use hatchling as build backend

**Rationale:** Lightweight, modern PEP 517 backend. Works well with `uv` and requires minimal configuration. No `setup.py` needed.

**Alternative considered:** `setuptools` — heavier, more configuration boilerplate.

### 3. Export public API from `__init__.py`

**Rationale:** Importing `Dashboard`, `DashboardConfig`, and `main` from the package root (`from stacktui import Dashboard`) provides a clean API surface if the package is used as a library.

## Risks / Trade-offs

- **`PROJECT_ROOT` resolution**: `Path(__file__).resolve().parent` now points to `stacktui/` instead of the repo root. This is correct for config search (falls back to parent), but should be verified with actual deployments.
- **Breaking change for direct invocation**: Users running `python dashboard.py` must switch to `uv run stacktui` or adjust their workflow. Mitigated by updating README documentation.
