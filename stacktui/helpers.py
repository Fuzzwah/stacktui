"""Helper functions for git, Docker, service queries, and config discovery."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from .config import PROJECT_ROOT, DashboardConfig

# ---------------------------------------------------------------------------
# Subprocess runner
# ---------------------------------------------------------------------------


def _run(cmd: list[str], timeout: int = 10) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


# ---------------------------------------------------------------------------
# Config discovery
# ---------------------------------------------------------------------------


def _detect_compose_project_name(compose_file: str) -> str | None:
    """Ask docker compose for the resolved project name."""
    out = _run(
        ["docker", "compose", "-f", compose_file, "config", "--format", "json"],
        timeout=10,
    )
    if out:
        try:
            return json.loads(out).get("name")
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def find_config(config_path: str | None = None) -> DashboardConfig:
    """Find and load the configuration file."""
    config: DashboardConfig | None = None

    if config_path:
        path = Path(config_path)
        if not path.exists():
            print(f"Error: Config file not found: {config_path}")
            sys.exit(1)
        config = DashboardConfig.load(path)

    if config is None:
        # Search in CWD (PROJECT_ROOT is also CWD)
        cwd_config = Path.cwd() / "dashboard.toml"
        if cwd_config.exists():
            config = DashboardConfig.load(cwd_config)

    if config is None:
        # Search next to the script (for running from source checkout)
        script_dir = Path(__file__).resolve().parent
        if script_dir != Path.cwd():
            script_config = script_dir / "dashboard.toml"
            if script_config.exists():
                config = DashboardConfig.load(script_config)

    if config is None:
        # Auto-copy a config if available.
        # Prefer demo config when the demo compose file exists, otherwise
        # fall back to the generic example template.
        cwd_config = Path.cwd() / "dashboard.toml"
        demo_candidates = [
            Path.cwd() / "demo" / "dashboard.toml",
            Path(__file__).resolve().parent / "demo" / "dashboard.toml",
        ]
        example_candidates = [
            Path.cwd() / "dashboard.toml.example",
            Path(__file__).resolve().parent / "dashboard.toml.example",
        ]
        for candidate in demo_candidates + example_candidates:
            if candidate.exists():
                import shutil
                shutil.copy2(candidate, cwd_config)
                print(f"Created dashboard.toml from {candidate} — edit it to match your project.")
                config = DashboardConfig.load(cwd_config)
                break

    if config is None:
        print("Error: No dashboard.toml or dashboard.toml.example found.")
        print("  Create a dashboard.toml and configure it.")
        sys.exit(1)

    # Auto-detect project name from docker compose if not set in config
    if not getattr(config, "_name_from_config", False):
        compose_file = str(PROJECT_ROOT / config.compose_dev)
        detected = _detect_compose_project_name(compose_file)
        if detected:
            config.project_name = detected

    return config


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------


def get_changed_files(old_sha: str, new_sha: str) -> list[str]:
    """Return list of files changed between two git SHAs."""
    out = _run(["git", "diff", "--name-only", f"{old_sha}..{new_sha}"], timeout=10)
    if not out:
        return []
    return [f.strip() for f in out.splitlines() if f.strip()]


def detect_affected_services(config: DashboardConfig, changed_files: list[str]) -> set[str]:
    """Map changed file paths to affected service names."""
    affected: set[str] = set()
    for filepath in changed_files:
        for prefix, service in config.path_map:
            if filepath.startswith(prefix) or filepath == prefix:
                if service is None:
                    return config.all_services
                affected.add(service)
                break
    return affected


def get_git_info() -> str:
    """Return 'branch@shortsha' or 'unknown'."""
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    sha = _run(["git", "rev-parse", "--short", "HEAD"])
    if branch and sha:
        return f"{branch}@{sha}"
    return "unknown"


def get_git_status_summary() -> str:
    """Return compact working-tree summary like '3M 1S 2?', 'clean', or '' on failure."""
    output = _run(["git", "status", "--porcelain"])
    if output is None or output == "":
        # Distinguish between clean (empty output) and failure (None→empty string from _run)
        # _run returns "" on failure, but also "" for clean repo — check if git works
        check = _run(["git", "rev-parse", "--git-dir"])
        if not check:
            return ""
        return "clean"
    staged = 0
    modified = 0
    untracked = 0
    for line in output.splitlines():
        if len(line) < 2:
            continue
        x, y = line[0], line[1]
        if x == "?" and y == "?":
            untracked += 1
        else:
            if x in "MADRC":
                staged += 1
            if y in "MD":
                modified += 1
    parts = []
    if modified:
        parts.append(f"{modified}M")
    if staged:
        parts.append(f"{staged}S")
    if untracked:
        parts.append(f"{untracked}?")
    return " ".join(parts) if parts else "clean"


def get_current_ref() -> str:
    """Return the current branch name, or short SHA if in detached HEAD."""
    ref = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    if ref and ref != "HEAD":
        return ref
    return _run(["git", "rev-parse", "--short", "HEAD"]) or "unknown"


def get_git_refs() -> list[tuple[str, str]]:
    """Return (display_label, ref_value) tuples: branches then recent commits."""
    options: list[tuple[str, str]] = []
    current = get_current_ref()

    branch_out = _run(["git", "branch", "-r", "--format=%(refname:short)"], timeout=10)
    if branch_out:
        for line in branch_out.splitlines():
            branch = line.strip()
            if not branch or branch.endswith("/HEAD") or "/" not in branch:
                continue
            short = branch.removeprefix("origin/")
            label = f"* {short}" if short == current else short
            options.append((label, short))

    log_out = _run(["git", "log", "--oneline", "-10"], timeout=10)
    if log_out:
        for line in log_out.splitlines():
            line = line.strip()
            if line:
                sha = line.split()[0]
                options.append((f"  {line}", sha))

    if not options:
        options.append(("(no refs available)", "unknown"))

    return options


# ---------------------------------------------------------------------------
# Docker / Compose helpers
# ---------------------------------------------------------------------------


def detect_prod_mode(config: DashboardConfig) -> bool:
    """Auto-detect production mode by checking for a running container."""
    if not config.prod_container:
        return False
    out = _run(["docker", "inspect", "--format", "{{.State.Status}}", config.prod_container])
    return out == "running"


def get_compose_file(config: DashboardConfig, prod: bool) -> str:
    """Return the compose file path for the current mode."""
    filename = config.compose_prod if prod else config.compose_dev
    return str(PROJECT_ROOT / filename)


def get_compose_cmd(compose_file: str) -> list[str]:
    """Return the base docker compose command with the right file."""
    return ["docker", "compose", "-f", compose_file]


def get_base_url(config: DashboardConfig, prod: bool) -> str:
    """Return the base URL for web links."""
    if prod and config.prod_url:
        return config.prod_url
    return config.dev_url


# ---------------------------------------------------------------------------
# Service data types
# ---------------------------------------------------------------------------


class ServiceInfo:
    """Parsed service status from docker compose ps."""

    def __init__(self, name: str, service: str, state: str, health: str, config: DashboardConfig | None = None, uptime_seconds: int | None = None, image: str = "") -> None:
        self.name = name
        self.service = service
        self.state = state
        self.health = health
        self._config = config
        self.uptime_seconds = uptime_seconds
        self.image = image

    @property
    def display_name(self) -> str:
        if self._config:
            return self._config.service_labels.get(self.service, self.service)
        return self.service

    @property
    def sort_key(self) -> int:
        """Return sort order: primary services first, then backend, then unknown."""
        if self._config:
            try:
                return self._config.service_order.index(self.service)
            except ValueError:
                return len(self._config.service_order)
        return 0

    @property
    def status_text(self) -> str:
        if self.health == "healthy":
            return "healthy"
        if self.health == "unhealthy":
            return "unhealthy"
        if self.health == "starting":
            return "starting"
        if self.state == "restarting":
            return "restarting"
        if self.state == "running":
            return "running"
        return self.state or "stopped"

    @property
    def uptime_text(self) -> str:
        if self.uptime_seconds is None:
            return ""
        return format_uptime(self.uptime_seconds)

    @property
    def image_tag(self) -> str:
        if not self.image or ":" not in self.image:
            return ""
        return self.image.rsplit(":", 1)[1]

    @property
    def color(self) -> str:
        s = self.status_text
        if s == "healthy":
            return "green"
        if s in ("running", "starting"):
            return "yellow"
        return "red"


def _parse_uptime(status: str) -> int | None:
    """Extract uptime in seconds from a Docker Status string like 'Up 3 hours'."""
    if not status or not status.startswith("Up "):
        return None
    s = status[3:].strip()
    # Remove health suffix like "(healthy)"
    paren = s.find("(")
    if paren != -1:
        s = s[:paren].strip()
    # Handle "About a minute", "About an hour"
    if s.startswith("About"):
        if "minute" in s:
            return 60
        if "hour" in s:
            return 3600
        return None
    # Handle "Less than a second"
    if s.startswith("Less"):
        return 0
    # Parse "<number> <unit>" patterns
    parts = s.split()
    if len(parts) < 2:
        return None
    try:
        n = int(parts[0])
    except ValueError:
        return None
    unit = parts[1].rstrip("s")
    multipliers = {"second": 1, "minute": 60, "hour": 3600, "day": 86400, "week": 604800, "month": 2592000}
    return n * multipliers.get(unit, 0) or None


def format_uptime(seconds: int) -> str:
    """Format seconds as compact duration text (e.g., '3d 4h', '23m', '45s')."""
    if seconds < 60:
        return f"{seconds}s"
    if seconds < 3600:
        return f"{seconds // 60}m"
    if seconds < 86400:
        h = seconds // 3600
        m = (seconds % 3600) // 60
        return f"{h}h {m}m" if m else f"{h}h"
    d = seconds // 86400
    h = (seconds % 86400) // 3600
    return f"{d}d {h}h" if h else f"{d}d"


# ---------------------------------------------------------------------------
# Service queries
# ---------------------------------------------------------------------------


def parse_services(config: DashboardConfig, compose_file: str) -> list[ServiceInfo]:
    """Query docker compose ps and parse the JSON output."""
    out = _run(
        [*get_compose_cmd(compose_file), "ps", "--format", "json", "-a"],
        timeout=15,
    )
    if not out:
        return []

    by_service: dict[str, ServiceInfo] = {}
    _state_priority = {"running": 3, "restarting": 2, "created": 1, "exited": 0, "dead": 0}

    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        name = obj.get("Name", obj.get("name", ""))
        service = obj.get("Service", obj.get("service", ""))
        state = obj.get("State", obj.get("state", ""))
        health = obj.get("Health", obj.get("health", ""))
        status = obj.get("Status", obj.get("status", ""))
        image = obj.get("Image", obj.get("image", ""))
        if not name:
            continue
        svc = ServiceInfo(name, service or name, state, health, config, _parse_uptime(status), image)
        key = svc.service
        if key not in by_service:
            by_service[key] = svc
        else:
            existing = by_service[key]
            existing_pri = _state_priority.get(existing.state, 0)
            new_pri = _state_priority.get(state, 0)
            if new_pri > existing_pri:
                by_service[key] = svc

    services = list(by_service.values())
    services.sort(key=lambda s: s.sort_key)
    return services


def parse_all_containers(config: DashboardConfig) -> list[ServiceInfo]:
    """Query all Docker containers for this project regardless of compose file."""
    prefix = f"{config.project_name}-"
    out = _run(
        ["docker", "ps", "-a", "--filter", f"name={prefix}", "--format",
         '{"Name":"{{.Names}}","State":"{{.State}}","Status":"{{.Status}}"}'],
        timeout=15,
    )
    if not out:
        return []

    by_service: dict[str, ServiceInfo] = {}
    _state_priority = {"running": 3, "restarting": 2, "created": 1, "exited": 0, "dead": 0}

    for line in out.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        name = obj.get("Name", "")
        if not name:
            continue
        service = name.removeprefix(prefix)
        service = service.removesuffix("-1")
        state = obj.get("State", "")
        status = obj.get("Status", "")
        health = ""
        if "(healthy)" in status:
            health = "healthy"
        elif "(unhealthy)" in status:
            health = "unhealthy"
        elif "(health: starting)" in status:
            health = "starting"
        svc = ServiceInfo(name, service, state, health, config)
        if service not in by_service:
            by_service[service] = svc
        else:
            existing_pri = _state_priority.get(by_service[service].state, 0)
            new_pri = _state_priority.get(state, 0)
            if new_pri > existing_pri:
                by_service[service] = svc

    services = list(by_service.values())
    services.sort(key=lambda s: s.sort_key)
    return services


def detect_native_processes(config: DashboardConfig) -> list[ServiceInfo]:
    """Detect services running as native Python processes (not in Docker)."""
    results: list[ServiceInfo] = []
    for name, pattern in config.native_processes:
        out = _run(["pgrep", "-f", pattern], timeout=5)
        if out.strip():
            results.append(ServiceInfo(f"native-{name}", name, "running", "", config))
    return results


# ---------------------------------------------------------------------------
# Freshness, errors, webhooks
# ---------------------------------------------------------------------------


def get_data_freshness(config: DashboardConfig) -> str:
    """Get data freshness from a container's healthcheck log."""
    container = config.freshness_container
    if not container:
        return "n/a"

    out = _run(
        ["docker", "inspect", "--format", "{{json .State.Health}}", container],
        timeout=10,
    )
    if not out:
        return "offline"
    try:
        health = json.loads(out)
    except json.JSONDecodeError:
        return "offline"

    if not health:
        return "offline"

    log_entries = health.get("Log", [])
    if not log_entries:
        return "offline"

    for entry in reversed(log_entries):
        if entry.get("ExitCode", 1) == 0:
            end_time_str = entry.get("End", "")
            if not end_time_str:
                continue
            try:
                end_time_str = end_time_str.split(".")[0] + "+00:00"
                end_time = datetime.fromisoformat(end_time_str)
                delta = datetime.now(UTC) - end_time
                total_seconds = int(delta.total_seconds())
                if total_seconds < 0:
                    return "just now"
                minutes = total_seconds // 60
                seconds = total_seconds % 60
                return f"{minutes}m {seconds:02d}s ago"
            except (ValueError, TypeError):
                continue

    return "unhealthy"


def get_error_counts(
    config: DashboardConfig, compose_file: str, running_services: list[str]
) -> dict[str, int]:
    """Scan recent Docker logs for error-level entries per service."""
    if not running_services:
        return {}

    pattern = re.compile(
        "|".join(re.escape(p) for p in config.error_patterns), re.IGNORECASE
    )
    counts: dict[str, int] = {}
    for svc in running_services:
        output = _run(
            ["docker", "compose", "-f", compose_file, "logs", "--tail=100", svc],
            timeout=10,
        )
        if output:
            counts[svc] = sum(1 for line in output.splitlines() if pattern.search(line))
        else:
            counts[svc] = 0
    return counts


WEBHOOK_SIGNAL_FILE: Path = Path()  # Set after config loads


def check_webhook_signal() -> dict | None:
    """Read the GitHub webhook signal file and return push info if new commits available."""
    if not WEBHOOK_SIGNAL_FILE.exists():
        return None

    try:
        data = json.loads(WEBHOOK_SIGNAL_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return None

    current_branch = get_current_ref()
    signal_branch = data.get("branch", "")
    if signal_branch != current_branch:
        return None

    local_head = _run(["git", "rev-parse", "HEAD"])
    remote_after = data.get("after", "")
    if local_head and remote_after and local_head.startswith(remote_after[:12]):
        return None

    return data


# ---------------------------------------------------------------------------
# Self-update utilities
# ---------------------------------------------------------------------------


def _is_installed_package() -> bool:
    """Return True if running from an installed package (not from source)."""
    return "site-packages" in str(Path(__file__).resolve())


def _get_stacktui_repo_root() -> Path | None:
    """Return the git repo root containing this StackTUI package, or None."""
    if _is_installed_package():
        return None
    current = Path(__file__).resolve().parent
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
    return None


def _check_stacktui_updates() -> int:
    """Check if the StackTUI repo is behind its upstream tracking branch.

    Returns the number of commits behind, or 0 on any failure.
    """
    repo = _get_stacktui_repo_root()
    if repo is None or repo == PROJECT_ROOT:
        return 0
    try:
        subprocess.run(
            ["git", "fetch"],
            capture_output=True, text=True, timeout=15, cwd=repo,
        )
        result = subprocess.run(
            ["git", "rev-list", "HEAD..@{u}", "--count"],
            capture_output=True, text=True, timeout=5, cwd=repo,
        )
        if result.returncode == 0:
            return int(result.stdout.strip())
    except (subprocess.TimeoutExpired, ValueError, OSError):
        pass
    return 0


def _get_script_relative_path() -> str:
    """Return the script's path relative to PROJECT_ROOT, for self-update detection."""
    if _is_installed_package():
        return ""
    try:
        return str(Path(__file__).resolve().relative_to(PROJECT_ROOT))
    except ValueError:
        return ""
