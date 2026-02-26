# StackTUI Greenfield Project Prompt

Use this prompt with Claude Code to scaffold a new Docker Compose project with StackTUI and OpenSpec from scratch.

Copy everything below the line and paste it as a prompt, filling in the placeholders.

---

## Prompt

Set up a new Docker Compose project with StackTUI dashboard and OpenSpec spec-driven workflow.

**Project details:**
- Project name: `<your-project-name>`
- Services: `<describe your services, e.g. "a Flask web app, a Celery worker, PostgreSQL, and Redis">`
- Dev base URL: `<e.g. http://localhost:8000>`

### Part 1: Project Structure

Create the basic project structure:

```
<project-name>/
  docker-compose.yml        # Docker Compose services
  dashboard.toml            # StackTUI configuration
  .gitignore
  logs/                     # Log directory
  <app directories...>      # Your application code
```

### Part 2: Add StackTUI

Add StackTUI as a git submodule:

```bash
git submodule add https://github.com/Fuzzwah/stacktui.git stacktui
```

Create `dashboard.toml` by copying `stacktui/dashboard.toml.example` and configuring it:

- `[project].name` — set to the project name (must match Docker Compose project name / container prefix)
- `[compose].dev` — path to docker-compose.yml
- `[services].primary` — app services with custom Dockerfiles (rebuilt with `--build` on restart, start after infra)
- `[services].infra` — infrastructure services using stock images (plain restart, start first)
- `[services.labels]` — friendly display names
- `[[path_map]]` — map source directory prefixes to the services they affect. Use `service = "*"` for files that affect all services
- `[logs].dir` — log directory (default: `logs`)
- `[links]` — useful URLs with `{base_url}` placeholder
- `[urls].dev` — the local dev base URL

Add to `.gitignore`:

```
.stacktui-user.toml
```

Add a convenience runner (Makefile target, justfile recipe, or shell script):

```bash
uv run --project stacktui stacktui --dev --config dashboard.toml
```

### Part 3: Set Up OpenSpec

OpenSpec is a spec-driven development workflow. It keeps a living specification of your system and structures changes through artifacts: proposal, specs, design, and tasks.

**Install OpenSpec CLI:**

```bash
npm install -g @fission-ai/openspec
```

**Initialize in the project:**

```bash
openspec init --tools claude
```

This creates the `openspec/` directory structure and installs Claude Code slash commands (`.claude/commands/opsx/`) for the full workflow:

| Command | What it does |
|---------|-------------|
| `/opsx:new <name>` | Start a new change, create artifacts step by step |
| `/opsx:ff <name>` | Fast-forward: create all artifacts at once |
| `/opsx:continue <name>` | Continue working on an existing change |
| `/opsx:apply <name>` | Implement tasks from a change |
| `/opsx:explore` | Think through problems (read-only, no code changes) |
| `/opsx:verify <name>` | Verify implementation matches artifacts |
| `/opsx:archive <name>` | Archive a completed change |
| `/opsx:sync <name>` | Sync delta specs to main specs |
| `/opsx:onboard` | Guided tutorial walkthrough |

**Add OpenSpec permissions to `.claude/settings.local.json`:**

```json
{
  "permissions": {
    "allow": [
      "Bash(openspec new change:*)",
      "Bash(openspec instructions:*)",
      "Bash(openspec status:*)"
    ]
  }
}
```

Merge these into any existing permissions in the file.

**Create initial specs:**

For each major capability in the project, create a spec file at `openspec/specs/<capability-name>/spec.md`. Use this format:

```markdown
# <Capability Name> Specification

## Purpose

<1-2 sentences describing what this capability does>

## Requirements

### Requirement: <requirement name>
<Description using SHALL/MUST for normative statements>

#### Scenario: <scenario name>
- **WHEN** <trigger condition>
- **THEN** <expected outcome>
```

Create specs for each service and cross-cutting concern (e.g. `web-app`, `worker`, `database`, `api-endpoints`, `authentication`). Keep them focused — one spec per distinct capability.

### Part 4: Document the workflow

Add this to the project's README:

```markdown
## Development Workflow

This project uses [OpenSpec](https://github.com/openspec-dev/openspec) for spec-driven development with [Claude Code](https://docs.anthropic.com/en/docs/claude-code).

**Making changes:**
1. `/opsx:ff <change-name>` — Create all planning artifacts (proposal, specs, design, tasks)
2. `/opsx:apply` — Implement the tasks
3. `/opsx:archive` — Archive the completed change and sync specs

**Other commands:** `/opsx:explore` to investigate, `/opsx:verify` to check implementation, `/opsx:onboard` for a guided tutorial.

Specs live in `openspec/specs/`. Change history is in `openspec/changes/archive/`.

## Dashboard

Run the StackTUI dashboard to monitor and manage services:

\`\`\`bash
<your convenience runner command here>
\`\`\`
```

### Notes

- **StackTUI auto-updates** on startup via `git pull --ff-only` on its submodule. Disable with `--no-update`
- **OpenSpec workflow**: proposal (why) → specs (what) → design (how) → tasks (checklist) → apply (implement) → archive
- **Specs stay in sync**: after archiving a change, delta specs merge into main specs so they always reflect the current system
- Run `/opsx:onboard` in Claude Code for a guided walkthrough of the complete workflow
