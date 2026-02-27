# StackTUI

A TUI dashboard for managing Docker Compose projects. Built with Python 3.11+ and Textual.

## Architecture

Python package split into focused modules under `stacktui/`:

### `config.py` — Configuration (`DashboardConfig`)
- Dataclass loaded from `dashboard.toml` (TOML format, stdlib `tomllib`)
- Searched in CWD first, then package's parent directory; `--config` flag overrides
- Services split into **primary** (app, rebuilt with `--build`) and **infra** (stock images, plain restart)
- `service_order` = primary + infra (determines display and startup order)
- Path-to-service mapping (`[[path_map]]`) drives git-aware affected service detection
- Defines `PROJECT_ROOT` and `USER_PREFS_FILENAME` constants

### `helpers.py` — Helper functions
- `_run()` — subprocess wrapper, returns stdout or empty string on failure
- `find_config()` — config file discovery and loading
- `detect_prod_mode()` — inspects a Docker container to auto-detect prod
- `get_git_info()`, `get_current_ref()`, `get_git_refs()` — git state queries
- `get_changed_files()`, `detect_affected_services()` — git diff to service mapping
- `ServiceInfo` — parsed service status data type
- `parse_services()` — queries `docker compose ps --format json`, deduplicates by service name
- `parse_all_containers()` — queries `docker ps` directly (cross-compose-file)
- `detect_native_processes()` — uses `pgrep -f` for non-Docker services (dev mode)
- `get_data_freshness()` — parses Docker healthcheck logs for time-since-last-success
- `check_webhook_signal()` — reads a JSON signal file for GitHub push notifications
- Self-update utilities (`_check_stacktui_updates()`, `_get_stacktui_repo_root()`, etc.)

### `widgets.py` — Textual widgets
- **`UpdateBanner`** (Horizontal) — shown when StackTUI has upstream updates available
- **`WebhookBanner`** (Static) — hidden by default, shown when webhook signal file has new commits
- **`ServicePanel`** (Vertical) — checkboxes + colored status dots for each service; auto-checks newly unhealthy services
- **`LinksPanel`** (Static) — renders links from config with `{base_url}` interpolation; dev-only links in dev mode

### `app.py` — Main App (`Dashboard`)
- **Layout**: Header → top-pane (3 columns: git/links, services, actions) → bottom-pane (log selector + RichLog) → Footer
- **Refresh loop**: `set_interval(10, _refresh_status)` polls Docker + freshness + webhook
- **Log tailing**: async tasks for Docker logs (`docker compose logs -f`) or file tailing (`tail -f` style)
- **Orchestration**: stop/start/restart run in `@work(thread=True)` workers, stream output to orchestration log + RichLog
- **Git operations**: pull, checkout, fetch refs — all threaded workers with orchestration logging

### `cli.py` — CLI entry point
- `_self_update()` — on startup, `git pull --ff-only`; re-execs if script changed
- `main()` — argument parsing, config loading, app launch

### `dashboard.py` — Backward-compat shim
- Re-exports all public symbols so `from stacktui.dashboard import ...` continues to work

### Service Orchestration Logic
- **Stop**: all selected services at once
- **Start**: infra first (`up -d`), then app services (`up -d`)
- **Restart**: infra gets `restart`, app services get `up -d --build`

## Key Patterns

- All Docker/git commands run via `_run()` in `helpers.py` (sync) or `_run_streaming()` on Dashboard (with live output)
- `PROJECT_ROOT = Path.cwd()` defined in `config.py` — all paths relative to working directory
- Import graph: `config` ← `helpers` ← `widgets` ← `app` ← `cli` (strictly acyclic)
- Orchestration actions write to both `RichLog` widget and `logs/orchestration.log` file
- `@work(exclusive=True, thread=True)` prevents concurrent orchestration operations
- Service dropdown dynamically combines running containers + configured log files

## Configuration Reference

See `dashboard.toml.example` for all options. Key sections:
- `[project]` — name (used for title + container prefix)
- `[compose]` — dev/prod compose file paths
- `[services]` — primary/infra lists + labels
- `[[path_map]]` — file prefix → service mapping
- `[logs]` — directory + named log files
- `[freshness]` — container for healthcheck monitoring
- `[links]` / `[links.dev_only]` — URL links with `{base_url}` templating
- `[urls]` — dev/prod base URLs
- `[prod_detection]` — container to inspect for auto-detection
- `[native_processes]` — pgrep patterns for non-Docker services

## Dependencies

- `textual >=1.0, <2.0` (only runtime dependency)
- Python 3.11+ (for `tomllib`, type unions, etc.)
- Docker with Compose v2
- Git

## Development

```bash
uv sync
uv run stacktui --dev          # run against local config
uv run stacktui --dev --config dashboard.toml  # explicit config
```

Demo environment: `docker compose -f demo/docker-compose.yml up -d`

## Project Structure

```
stacktui/                 # Python package
  __init__.py             # Public API exports (Dashboard, DashboardConfig, main)
  config.py               # Configuration dataclass + constants
  helpers.py              # Git, Docker, service query helpers
  widgets.py              # Textual widget classes
  app.py                  # Dashboard(App) main application
  cli.py                  # CLI entry point + self-update
  dashboard.py            # Backward-compat re-export shim
dashboard.toml            # Active config (demo preset)
dashboard.toml.example    # Annotated config template
pyproject.toml            # Package metadata + build config
demo/                     # Demo Docker Compose environment
  docker-compose.yml      # 5-service stack (webapp, worker, nginx, db, redis)
  webapp/                 # Flask app with healthcheck
  worker/                 # Background job processor
  nginx/                  # Reverse proxy config
  send_webhook.py         # Simulate GitHub push webhook
openspec/                 # OpenSpec specs and changes
```

## Keyboard Shortcuts

| Key | Action              |
|-----|---------------------|
| q   | Quit                |
| r   | Refresh status      |
| g   | Git pull            |
| s   | Stop selected       |
| t   | Start selected      |
| p   | Restart selected    |
| b   | Rebuild selected    |
| l   | Focus log selector  |
| T   | Cycle theme         |

## OpenSpec

Project specs live in `openspec/specs/`. Use `/opsx:propose` to create a spec-driven change with all artifacts in one step.

**Workflow rule:** When entering plan mode for any non-trivial implementation task, always propose using `/opsx:propose` to the user before exiting plan mode. The OpenSpec workflow ensures changes are spec-driven with proper artifacts (proposal, delta specs, design, task list) before code is written. Do not exit plan mode and jump straight to implementation — route through `/opsx:propose` instead.

**Core commands:**
- `/opsx:propose` — Create a complete change proposal (proposal + specs + design + tasks)
- `/opsx:explore` — Investigate problems, clarify requirements (no code)
- `/opsx:apply` — Implement tasks from a change
- `/opsx:archive` — Archive a completed change and sync specs
