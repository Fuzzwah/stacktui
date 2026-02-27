# StackTUI

A TUI dashboard for Docker Compose projects.

Monitor services, tail logs, manage deployments, and control your stack from one terminal.

## Themes

StackTUI supports 12 color themes. Press `T` to cycle through them, or use the command palette (`Ctrl+P`).

![textual-dark](docs/screenshots/textual-dark.svg)
![nord](docs/screenshots/nord.svg)
![gruvbox](docs/screenshots/gruvbox.svg)
![tokyo-night](docs/screenshots/tokyo-night.svg)

<details>
<summary>All available themes</summary>

catppuccin-latte, catppuccin-mocha, dracula, flexoki, gruvbox, monokai, nord, solarized-light, textual-ansi, textual-dark, textual-light, tokyo-night

</details>

## Features

- **Service monitoring** — Live health indicators (healthy/running/stopped) with colored status dots, refreshed every 10 seconds; includes healthcheck freshness tracking showing time since last successful check
- **Container uptime** — Compact duration display (e.g., "3d 4h") next to status indicators to spot unexpected restarts at a glance
- **Restart counts** — Per-container restart count highlighting services caught in restart loops
- **Resource usage** — Per-service CPU and memory usage displayed in the service panel for early detection of runaway processes
- **Image versions** — Docker image tags shown next to infrastructure services (e.g., `postgres:16.2`, `redis:7.4`)
- **Port mappings** — Exposed ports displayed next to each service (e.g., `:8000`, `:5432`)
- **Log error counts** — Badges showing recent ERROR/CRITICAL log line counts per service without manual tailing
- **Log tailing** — Real-time streaming from Docker containers or local log files, switchable via dropdown
- **Service orchestration** — Stop, start, restart, and rebuild selected services with smart ordering (infra first, then app services with `--build`)
- **Orchestration history** — Compact list of recent orchestration actions with timestamps
- **Service selection** — Checkbox-based selection with quick-select modes (All, Changed, Stopped, Running, None) and auto-selection of affected/unhealthy services
- **Git integration** — Pull, checkout, browse refs, view history, and auto-detect affected services from diffs
- **Git status summary** — Uncommitted change counts (modified, staged, untracked) in the git info area
- **Webhook notifications** — Banner alerts when GitHub pushes new commits to the current branch
- **Theme switching** — 12 built-in themes, cycle with `T` or pick from the command palette; persisted per-user across sessions
- **User preferences** — Per-user settings in `.stacktui-user.toml` (not committed to version control) overlaying project config
- **Self-update check** — Background check for upstream updates with in-app banner notification and reload button
- **Dev/prod modes** — Auto-detects environment via container inspection, or use `--prod`/`--dev` flags
- **Native process detection** — Monitors non-Docker processes via `pgrep` patterns (dev mode only)
- **TOML configuration** — One config file adapts the dashboard to any Docker Compose project

## Quick Start

```bash
# Clone the repo
git clone https://github.com/fuzzwah/stacktui.git
cd stacktui

# Start the demo services
docker compose -f demo/docker-compose.yml up -d

# Install and run with the demo config
uv sync
cp demo/dashboard.toml dashboard.toml
uv run stacktui --dev
```

Visit <http://localhost:8080> to generate some nginx/webapp logs.

## Installation

```bash
pip install stacktui
# or with uv
uv add stacktui
```

## Use With Your Project

1. Copy `dashboard.toml.example` to `dashboard.toml` in your project root
2. Configure your services, log files, and links
3. Run it: `stacktui` (or `uv run stacktui`)

See `dashboard.toml.example` for a fully annotated configuration reference.

### Coding Agent Prompts

If you use a coding agent (Claude Code, Cursor, etc.), these ready-made prompts will set things up for you:

- **[`INTEGRATION_PROMPT.md`](INTEGRATION_PROMPT.md)** — Add StackTUI to an existing Docker Compose project. Walks the agent through adding StackTUI as a git submodule, creating a `dashboard.toml`, and setting up a convenience runner.

- **[`GREENFIELD_PROMPT.md`](GREENFIELD_PROMPT.md)** — Start a new project from scratch with StackTUI and [OpenSpec](https://github.com/openspec-dev/openspec). Includes full project scaffolding, Docker Compose setup, dashboard config, and the spec-driven development workflow with Claude Code slash commands.

## Keyboard Shortcuts

| Key | Action |
| --- | --- |
| `q` | Quit |
| `r` | Refresh status |
| `g` | Git pull |
| `s` | Stop selected services |
| `t` | Start selected services |
| `p` | Restart selected services |
| `b` | Rebuild selected services |
| `l` | Focus log service selector |
| `T` | Cycle theme |

## Configuration

The dashboard reads from `dashboard.toml` (searched in CWD, then the package's parent directory). Use `--config path/to/file.toml` to specify a custom path.

Key sections:

- **`[project]`** — Project name (used for title and container name prefix)
- **`[compose]`** — Paths to dev/prod compose files
- **`[services]`** — Primary (app) and infra service lists with display labels
- **`[[path_map]]`** — Maps source file paths to services (for git-aware affected service detection)
- **`[logs]`** — Log directory, named log files, and error patterns for badge counts
- **`[freshness]`** — Container to probe for healthcheck freshness
- **`[links]`** — URLs shown in the links panel (`{base_url}` placeholder supported)
- **`[links.dev_only]`** — Dev-only links (hidden in production mode)
- **`[urls]`** — Base URLs for dev and prod modes
- **`[prod_detection]`** — Container to check for auto-detecting production mode
- **`[theme]`** — Default theme name on startup
- **`[native_processes]`** — pgrep patterns for non-Docker service detection (dev mode only)

## Demo Environment

The `demo/` directory contains a complete example with 5 services:

| Service | Type | Description |
| --- | --- | --- |
| **webapp** | App | Flask web app with healthcheck |
| **worker** | App | Background job processor (logs to file + stdout) |
| **nginx** | Infra | Reverse proxy to webapp |
| **db** | Infra | PostgreSQL 16 |
| **redis** | Infra | Redis 7 |

Test the webhook banner: `python demo/send_webhook.py`

## Development

```bash
git clone https://github.com/fuzzwah/stacktui.git
cd stacktui
uv sync
uv run stacktui --dev
```

### Workflow

This project is built with [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [OpenSpec](https://github.com/openspec-dev/openspec), a spec-driven development workflow.

**How it works:**

1. **Specs describe the system** — Each major capability has a specification in `openspec/specs/` (e.g., service monitoring, log tailing, git integration). Specs define requirements, not implementation details.

2. **Changes go through artifacts** — New features follow a structured flow: proposal → design → delta specs → task list → implementation. Each artifact builds on the previous one. See `openspec/changes/archive/` for completed examples.

3. **Claude Code implements from specs** — Claude Code reads the specs and task lists, then writes the code. The specs act as a shared understanding between human and AI, keeping implementations grounded in documented requirements.

4. **Specs stay in sync** — After a change is implemented and verified, its delta specs merge into the main specs, and the change is archived. The specs always reflect the current state of the system.

The `openspec/` directory contains the full spec history. The `.claude/` directory contains the Claude Code skills that drive the workflow.

### Project Structure

```text
stacktui/                 # Python package
  __init__.py             # Public API exports
  config.py               # Configuration dataclass + constants
  helpers.py              # Git, Docker, service query helpers
  widgets.py              # Textual widget classes
  app.py                  # Dashboard(App) main application
  cli.py                  # CLI entry point + self-update
  dashboard.py            # Backward-compat re-export shim
dashboard.toml.example    # Annotated config template
pyproject.toml            # Package metadata + build config
demo/                     # Demo Docker Compose environment
  dashboard.toml          # Pre-configured demo config
  docker-compose.yml      # 5-service demo stack
openspec/                 # OpenSpec specs and changes
```

## Requirements

- Python 3.11+
- [Textual](https://github.com/Textualize/textual) >=1.0, <2.0
- [tomlkit](https://github.com/sdispater/tomlkit) >=0.13 (format-preserving TOML writes)
- Docker with Compose v2
- Git

## License

MIT
