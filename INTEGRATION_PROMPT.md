# StackTUI Integration Prompt

Use this prompt with a coding agent (Claude Code, Cursor, etc.) to add StackTUI to your Docker Compose project.

Copy everything below the line and paste it as a prompt, replacing the placeholder with your repo URL.

---

## Prompt

Add StackTUI as a git submodule to this project. StackTUI is a TUI dashboard for managing Docker Compose projects.

**Step 1: Add the submodule**

```
git submodule add https://github.com/Fuzzwah/stacktui.git stacktui
```

**Step 2: Create `dashboard.toml`**

Copy `stacktui/dashboard.toml.example` to `dashboard.toml` in the project root and configure it for this project:

- `[project].name` — set to the project name. This must match the Docker Compose project name (the container prefix, e.g. if containers are `myapp-webapp-1` then name is `myapp`)
- `[compose].dev` — path to the docker-compose.yml file (relative to project root)
- `[compose].prod` — path to the production compose file if one exists (optional)
- `[services].primary` — list of app services that have custom Dockerfiles. These get rebuilt with `--build` on restart and start after infra services
- `[services].infra` — list of infrastructure services using stock images (e.g. db, redis, nginx). These get a plain restart and start first
- `[services.labels]` — friendly display names for each service
- `[[path_map]]` entries — map source directory prefixes to the services they affect. This powers the "Changed" service filter based on git diffs. Use `service = "*"` for files that affect all services (e.g. docker-compose.yml). Look at the project structure to determine which directories map to which services
- `[logs].dir` — set the log directory (default: `logs`)
- `[logs.files]` — named log files that can be tailed in the dashboard
- `[links]` — useful URLs using `{base_url}` as a placeholder (e.g. `"Admin" = "{base_url}/admin/"`)
- `[links.dev_only]` — links only shown in dev mode (e.g. Mailpit, pgAdmin)
- `[urls].dev` — the local dev base URL (e.g. `http://localhost:8000`)
- `[urls].prod` — the production base URL (optional)
- `[prod_detection].container` — container name to inspect for auto-detecting production mode (optional)
- `[freshness].container` — container to probe for healthcheck freshness display (optional, requires healthcheck configured)
- `[native_processes]` — pgrep patterns for services run outside Docker during development (optional)

**Step 3: Update `.gitignore`**

Add this line:

```
.stacktui-user.toml
```

This file stores per-user preferences (selected theme) and should not be committed.

**Step 4: Create a convenience runner**

Add one of these to your project's Makefile, justfile, or scripts:

```bash
# If using uv (recommended)
uv run --project stacktui stacktui --dev --config dashboard.toml

# If using pip
pip install -e stacktui && stacktui --dev --config dashboard.toml
```

**Step 5: Ensure the logs directory exists**

Create the directory specified in `[logs].dir` if it doesn't already exist:

```bash
mkdir -p logs
```

**Notes:**
- StackTUI auto-updates itself on startup by running `git pull --ff-only` on its submodule. Disable with the `--no-update` CLI flag
- Primary services start after infra services and get rebuilt with `--build` on restart
- The `[[path_map]]` section is optional but enables git-aware features (detecting which services are affected by code changes)
- Use `--prod` or `--dev` flags to force a mode, or configure `[prod_detection]` for auto-detection
- Requires Python 3.11+, Docker with Compose v2, and Git
