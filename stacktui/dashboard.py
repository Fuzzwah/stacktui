#!/usr/bin/env python3
"""StackTUI — A TUI dashboard for Docker Compose projects.

Monitor services, tail logs, and manage deployments from one terminal.

Usage:
    python dashboard.py                     # auto-detect environment
    python dashboard.py --prod              # force production mode
    python dashboard.py --dev               # force development mode
    python dashboard.py --config my.toml    # use a specific config file
"""

from __future__ import annotations

import argparse
import asyncio
import contextlib
import json
import os
import subprocess
import sys
import tomllib
import tomlkit
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import ClassVar

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import (
    Button,
    Checkbox,
    Footer,
    Header,
    RichLog,
    Select,
    Static,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path.cwd()
USER_PREFS_FILENAME = ".stacktui-user.toml"


@dataclass
class DashboardConfig:
    """Configuration loaded from dashboard.toml."""

    project_name: str = "myproject"

    # Compose files
    compose_dev: str = "docker-compose.yml"
    compose_prod: str = "docker-compose.prod.yml"

    # Service topology
    primary_services: list[str] = field(default_factory=list)
    infra_services: list[str] = field(default_factory=list)
    service_labels: dict[str, str] = field(default_factory=dict)

    # Path-to-service mapping for "Changed" restart mode
    path_map: list[tuple[str, str | None]] = field(default_factory=list)

    # Logs
    logs_dir: Path = field(default_factory=lambda: PROJECT_ROOT / "logs")
    log_files: dict[str, Path] = field(default_factory=dict)

    # Freshness monitoring
    freshness_container: str = ""

    # Links
    links: dict[str, str] = field(default_factory=dict)
    dev_links: dict[str, str] = field(default_factory=dict)

    # URLs
    dev_url: str = "http://localhost:8000"
    prod_url: str = ""

    # Production detection
    prod_container: str = ""

    # Native process detection (dev mode)
    native_processes: list[tuple[str, str]] = field(default_factory=list)

    # Theme
    theme_name: str = "nord"

    # Source file path (for write-back)
    config_path: Path | None = None
    # User preferences file path (for per-user overrides)
    user_prefs_path: Path | None = None

    @property
    def service_order(self) -> list[str]:
        return self.primary_services + self.infra_services

    @property
    def app_services(self) -> set[str]:
        return set(self.primary_services)

    @property
    def infra_service_set(self) -> set[str]:
        return set(self.infra_services)

    @property
    def all_services(self) -> set[str]:
        return self.app_services | self.infra_service_set

    @classmethod
    def load(cls, path: Path) -> DashboardConfig:
        """Load configuration from a TOML file."""
        with open(path, "rb") as f:
            data = tomllib.load(f)

        config = cls()

        # [project]
        project = data.get("project", {})
        config.project_name = project.get("name", config.project_name)
        config._name_from_config = "name" in project

        # [compose]
        compose = data.get("compose", {})
        config.compose_dev = compose.get("dev", config.compose_dev)
        config.compose_prod = compose.get("prod", config.compose_prod)

        # [services]
        services = data.get("services", {})
        config.primary_services = services.get("primary", [])
        config.infra_services = services.get("infra", [])
        config.service_labels = services.get("labels", {})

        # [[path_map]]
        for entry in data.get("path_map", []):
            prefix = entry.get("prefix", "")
            service = entry.get("service", "")
            # "*" or empty string means "all services"
            if service in ("*", ""):
                config.path_map.append((prefix, None))
            else:
                config.path_map.append((prefix, service))

        # [logs]
        logs = data.get("logs", {})
        logs_dir_str = logs.get("dir", "logs")
        config.logs_dir = PROJECT_ROOT / logs_dir_str
        for name, filename in logs.get("files", {}).items():
            config.log_files[name] = config.logs_dir / filename

        # [freshness]
        freshness = data.get("freshness", {})
        config.freshness_container = freshness.get("container", "")

        # [links]
        links_data = data.get("links", {})
        # Separate dev_only from regular links
        config.dev_links = {}
        config.links = {}
        for key, value in links_data.items():
            if key == "dev_only":
                config.dev_links = value if isinstance(value, dict) else {}
            else:
                config.links[key] = value

        # [urls]
        urls = data.get("urls", {})
        config.dev_url = urls.get("dev", config.dev_url)
        config.prod_url = urls.get("prod", "")

        # [prod_detection]
        prod_det = data.get("prod_detection", {})
        config.prod_container = prod_det.get("container", "")

        # [native_processes]
        native = data.get("native_processes", {})
        config.native_processes = [(name, pattern) for name, pattern in native.items()]

        # [theme]
        theme = data.get("theme", {})
        config.theme_name = theme.get("name", "") or config.theme_name

        # Track source file for write-back
        config.config_path = path

        # Load per-user preferences (overrides project config)
        user_prefs_file = path.parent / USER_PREFS_FILENAME
        config.user_prefs_path = user_prefs_file
        if user_prefs_file.exists():
            with open(user_prefs_file, "rb") as uf:
                user_data = tomllib.load(uf)
            user_theme = user_data.get("theme", {}).get("name", "")
            if user_theme:
                config.theme_name = user_theme

        return config

    def save_theme(self, theme_name: str) -> None:
        """Save the theme name to the per-user preferences file."""
        if self.user_prefs_path is None:
            return
        if self.user_prefs_path.exists():
            doc = tomlkit.parse(self.user_prefs_path.read_text())
        else:
            doc = tomlkit.document()
            doc.add(tomlkit.comment("Per-user StackTUI preferences (not committed to git)"))
            doc.add(tomlkit.nl())
        if "theme" not in doc:
            doc.add("theme", tomlkit.table())
        doc["theme"]["name"] = theme_name
        self.user_prefs_path.write_text(tomlkit.dumps(doc))


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
        # Auto-copy the example config if available
        cwd_config = Path.cwd() / "dashboard.toml"
        example_candidates = [
            Path.cwd() / "dashboard.toml.example",
            Path(__file__).resolve().parent / "dashboard.toml.example",
        ]
        for example in example_candidates:
            if example.exists():
                import shutil
                shutil.copy2(example, cwd_config)
                print(f"Created dashboard.toml from {example.name} — edit it to match your project.")
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
# Helpers
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


def _run(cmd: list[str], timeout: int = 10) -> str:
    """Run a command and return stdout, or empty string on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout, cwd=PROJECT_ROOT
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


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


def detect_prod_mode(config: DashboardConfig) -> bool:
    """Auto-detect production mode by checking for a running container."""
    if not config.prod_container:
        return False
    out = _run(["docker", "inspect", "--format", "{{.State.Status}}", config.prod_container])
    return out == "running"


def get_git_info() -> str:
    """Return 'branch@shortsha' or 'unknown'."""
    branch = _run(["git", "rev-parse", "--abbrev-ref", "HEAD"])
    sha = _run(["git", "rev-parse", "--short", "HEAD"])
    if branch and sha:
        return f"{branch}@{sha}"
    return "unknown"


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
# Data types
# ---------------------------------------------------------------------------


class ServiceInfo:
    """Parsed service status from docker compose ps."""

    def __init__(self, name: str, service: str, state: str, health: str, config: DashboardConfig | None = None) -> None:
        self.name = name
        self.service = service
        self.state = state
        self.health = health
        self._config = config

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
    def color(self) -> str:
        s = self.status_text
        if s == "healthy":
            return "green"
        if s in ("running", "starting"):
            return "yellow"
        return "red"


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
        if not name:
            continue
        svc = ServiceInfo(name, service or name, state, health, config)
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
# Widgets
# ---------------------------------------------------------------------------


class UpdateBanner(Static):
    """Notification banner shown when StackTUI has upstream updates available."""

    DEFAULT_CSS = """
    UpdateBanner {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
        background: $primary-darken-2;
        color: $text;
        display: none;
    }
    UpdateBanner.visible {
        display: block;
    }
    """

    def show_update(self, count: int) -> None:
        """Update banner with commit count and make it visible."""
        line = Text()
        line.append(f" StackTUI update available ", style="bold")
        line.append(f"({count} commit{'s' if count != 1 else ''} behind)", style="")
        line.append(" — restart to update", style="italic")
        self.update(line)
        self.add_class("visible")

    def hide(self) -> None:
        """Hide the banner."""
        self.remove_class("visible")


class WebhookBanner(Static):
    """Notification banner shown when GitHub webhook reports new commits."""

    DEFAULT_CSS = """
    WebhookBanner {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
        background: $warning-darken-2;
        color: $text;
        display: none;
    }
    WebhookBanner.visible {
        display: block;
    }
    """

    def show_push(self, data: dict) -> None:
        """Update banner with push data and make it visible."""
        commits = data.get("commits", [])
        count = len(commits)
        pusher = data.get("pusher", "someone")
        latest_msg = commits[-1]["message"] if commits else "new changes"

        line = Text()
        line.append(f" {count} new commit{'s' if count != 1 else ''}", style="bold yellow")
        line.append(f" from {pusher}: ", style="")
        line.append(latest_msg, style="italic")

        self.update(line)
        self.add_class("visible")

    def hide(self) -> None:
        """Hide the banner."""
        self.remove_class("visible")


class ServicePanel(Vertical):
    """Displays service status with inline checkboxes."""

    def __init__(self, config: DashboardConfig, **kwargs: object) -> None:
        super().__init__(**kwargs)
        self._config = config
        self._prev_unhealthy: set[str] = set()
        self._service_statuses: dict[str, str] = {}

    def compose(self) -> ComposeResult:
        yield Static("Services", id="services-title")
        yield Static("", id="data-freshness")
        for svc in self._config.service_order:
            label = self._config.service_labels.get(svc, svc)
            with Horizontal(classes="service-row"):
                yield Checkbox(label, id=f"chk-{svc}")
                yield Static("", id=f"status-{svc}", classes="service-status")

    def update_services(self, services: list[ServiceInfo], freshness: str) -> None:
        svc_map = {s.service: s for s in services}
        current_unhealthy: set[str] = set()
        statuses: dict[str, str] = {}

        for svc in self._config.service_order:
            info = svc_map.get(svc)
            status_widget = self.query_one(f"#status-{svc}", Static)

            if info:
                line = Text()
                line.append("● ", style=info.color)
                line.append(info.status_text, style=info.color)
                status_widget.update(line)
                statuses[svc] = info.status_text

                if info.status_text not in ("healthy", "running"):
                    current_unhealthy.add(svc)
            else:
                status_widget.update(Text("—", style="dim"))
                statuses[svc] = ""

        self._service_statuses = statuses

        newly_unhealthy = current_unhealthy - self._prev_unhealthy
        for svc in newly_unhealthy:
            self.query_one(f"#chk-{svc}", Checkbox).value = True
        self._prev_unhealthy = current_unhealthy

        freshness_widget = self.query_one("#data-freshness", Static)
        freshness_line = Text()
        freshness_line.append("Freshness: ", style="bold")
        if freshness in ("offline", "unhealthy"):
            freshness_line.append(freshness, style="red")
        elif freshness == "n/a":
            freshness_line.append(freshness, style="dim")
        else:
            freshness_line.append(freshness, style="green")
        freshness_widget.update(freshness_line)

    def get_unhealthy_services(self) -> set[str]:
        """Return services that are not healthy or running."""
        return {
            svc for svc, status in self._service_statuses.items()
            if status not in ("healthy", "running")
        }

    def get_service_status(self, svc: str) -> str:
        """Return the current status text for a service."""
        return self._service_statuses.get(svc, "")


class LinksPanel(Static):
    """Displays clickable links."""

    def set_links(self, config: DashboardConfig, base_url: str, prod: bool) -> None:
        lines: list[Text] = []
        lines.append(Text("Links", style="bold underline"))
        lines.append(Text(""))

        all_links: list[tuple[str, str]] = []
        for label, url_template in config.links.items():
            url = url_template.replace("{base_url}", base_url)
            all_links.append((label, url))

        if not prod:
            for label, url_template in config.dev_links.items():
                url = url_template.replace("{base_url}", base_url)
                all_links.append((label, url))

        for label, url in all_links:
            line = Text()
            line.append(f"  {label}: ", style="bold")
            line.append(url, style="underline cyan")
            lines.append(line)

        combined = Text("\n").join(lines)
        self.update(combined)


# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------


class Dashboard(App):
    """StackTUI — Docker Compose Dashboard."""

    CSS: ClassVar[str] = """
    #top-pane {
        height: 1fr;
        border-bottom: solid $accent;
    }

    #col-services {
        width: 1fr;
        padding: 1;
        border-right: solid $accent;
    }

    #col-git {
        width: 1fr;
        padding: 1;
        border-right: solid $accent;
    }

    #col-actions {
        width: 1fr;
        padding: 1;
    }

    #bottom-pane {
        height: 1fr;
        padding: 0 1;
    }

    #service-panel {
        height: auto;
        margin-bottom: 1;
    }

    #services-title {
        text-style: bold underline;
        margin-bottom: 0;
    }

    .service-row {
        height: 1;
    }

    .service-row Checkbox {
        height: 1;
        padding: 0;
        margin: 0;
        width: 1fr;
        border: none;
    }

    .service-status {
        height: 1;
        width: auto;
        padding: 0;
        margin: 0;
    }

    #data-freshness {
        height: auto;
        margin-top: 1;
    }

    #links-panel {
        height: auto;
        margin-bottom: 1;
    }

    #git-controls {
        height: auto;
        dock: bottom;
    }

    #ref-select {
        width: 100%;
        margin-bottom: 1;
    }

    .actions-title {
        text-style: bold underline;
        margin-bottom: 1;
    }

    #selection-mode {
        width: 100%;
        margin-top: 1;
    }

    #btn-stop {
        width: 100%;
        margin-bottom: 1;
    }

    #btn-start {
        width: 100%;
        margin-bottom: 1;
    }

    #btn-restart {
        width: 100%;
        margin-bottom: 1;
    }

    #btn-stop.hidden {
        display: none;
    }

    #btn-start.hidden {
        display: none;
    }

    #btn-restart.hidden {
        display: none;
    }

    #btn-reload {
        width: 100%;
        margin-top: 1;
    }

    #btn-reload.hidden {
        display: none;
    }

    #btn-git-pull {
        width: 100%;
        dock: bottom;
    }

    #service-select {
        width: 100%;
        margin-bottom: 1;
    }

    #log-view {
        border: solid $accent;
    }
    """

    BINDINGS: ClassVar[list[Binding]] = [
        Binding("q", "quit", "Quit"),
        Binding("r", "refresh", "Refresh"),
        Binding("g", "git_pull", "Git Pull"),
        Binding("s", "stop", "Stop"),
        Binding("t", "start", "Start"),
        Binding("p", "restart", "Restart"),
        Binding("l", "focus_logs", "Logs"),
        Binding("T", "next_theme", "Theme"),
    ]

    def __init__(self, config: DashboardConfig, prod: bool | None = None) -> None:
        super().__init__()
        self._config = config
        self.title = f"{config.project_name} Dashboard"
        if prod is None:
            self._prod = detect_prod_mode(config)
        else:
            self._prod = prod
        self._compose_file = get_compose_file(config, self._prod)
        self._base_url = get_base_url(config, self._prod)
        self._git_info = get_git_info()
        self._log_task: asyncio.Task[None] | None = None
        self._log_process: asyncio.subprocess.Process | None = None
        self._orch_in_progress = False
        self._affected_services: set[str] = set()

    def compose(self) -> ComposeResult:
        yield Header()

        with Horizontal(id="top-pane"):
            with Vertical(id="col-git"):
                yield UpdateBanner(id="update-banner")
                yield LinksPanel(id="links-panel")
                yield WebhookBanner(id="webhook-banner")
                with Vertical(id="git-controls"):
                    yield Select(
                        get_git_refs(),
                        prompt="Git ref",
                        allow_blank=True,
                        value=get_current_ref(),
                        id="ref-select",
                    )
                    yield Button("Git Pull", id="btn-git-pull", variant="primary")
            with VerticalScroll(id="col-services"):
                yield ServicePanel(self._config, id="service-panel")
                yield Select(
                    [("All", "all"), ("Changed", "changed"), ("Stopped", "stopped"),
                     ("Running", "running"), ("None", "none")],
                    prompt="Select services",
                    allow_blank=True,
                    value=Select.BLANK,
                    id="selection-mode",
                )
            with Vertical(id="col-actions"):
                yield Static("Actions", classes="actions-title")
                yield Button("Restart", id="btn-restart", variant="warning", classes="hidden")
                yield Button("Stop", id="btn-stop", variant="error", classes="hidden")
                yield Button("Start", id="btn-start", variant="success", classes="hidden")
                yield Button("Reload Dashboard", id="btn-reload", variant="success", classes="hidden")

        with Vertical(id="bottom-pane"):
            yield Select(
                self._get_service_options(),
                prompt="Select service",
                allow_blank=False,
                value=self._default_log_service(),
                id="service-select",
            )
            yield RichLog(
                id="log-view",
                highlight=True,
                markup=True,
                max_lines=2000,
                wrap=True,
                auto_scroll=True,
            )

        yield Footer()

    def on_mount(self) -> None:
        if self._config.theme_name in self.available_themes:
            self.theme = self._config.theme_name

        mode = "prod" if self._prod else "dev"
        self.sub_title = f"{mode} | {self._git_info}"

        links = self.query_one("#links-panel", LinksPanel)
        links.set_links(self._config, self._base_url, self._prod)

        self._refresh_status()
        self._fetch_and_refresh_refs()
        self.set_interval(10, self._refresh_status)
        self._check_for_self_update()
        self.set_interval(300, self._check_for_self_update)
        self._start_log_tail(self._default_log_service())

    def _get_service_options(self) -> list[tuple[str, str]]:
        """Get service options from running containers + available log files."""
        container_options: list[tuple[str, str, int]] = []
        seen_services: set[str] = set()

        for svc in parse_all_containers(self._config):
            container_options.append((svc.display_name, svc.service, svc.sort_key))
            seen_services.add(svc.service)

        container_options.sort(key=lambda x: x[2])

        options: list[tuple[str, str]] = []

        # Orchestration log always first (if it exists)
        orch_path = self._config.logs_dir / "orchestration.log"
        if orch_path.exists():
            options.append(("Orchestration", "file:orchestration"))

        for label, service, _sort_key in container_options:
            options.append((label, service))

        for name, path in self._config.log_files.items():
            if path.exists() and name not in seen_services:
                label = f"{name} (log file)"
                options.append((label, f"file:{name}"))

        if not options:
            for svc in self._config.service_order[:3]:
                options.append((self._config.service_labels.get(svc, svc), svc))

        return options

    def _default_log_service(self) -> str:
        """Default service to tail logs from."""
        options = self._get_service_options()
        # Prefer first primary service
        for _label, value in options:
            for primary in self._config.primary_services:
                if primary in value:
                    return value
        return options[0][1] if options else self._config.service_order[0] if self._config.service_order else "db"

    def _refresh_status(self) -> None:
        """Refresh service status and data freshness."""
        services = parse_services(self._config, self._compose_file)

        if not self._prod:
            docker_names = {s.display_name for s in services}
            for native in detect_native_processes(self._config):
                if native.display_name not in docker_names:
                    services.append(native)

        freshness = get_data_freshness(self._config) if self._prod else "n/a"
        panel = self.query_one("#service-panel", ServicePanel)
        panel.update_services(services, freshness)

        self._update_action_visibility()

        banner = self.query_one("#webhook-banner", WebhookBanner)
        signal = check_webhook_signal()
        if signal:
            banner.show_push(signal)
        else:
            banner.hide()

    # -- Self-update check -------------------------------------------------

    @work(thread=True)
    def _check_for_self_update(self) -> None:
        """Check if StackTUI has upstream updates available."""
        count = _check_stacktui_updates()
        banner = self.query_one("#update-banner", UpdateBanner)
        if count > 0:
            self.call_from_thread(banner.show_update, count)
        else:
            self.call_from_thread(banner.hide)

    # -- Log tailing -------------------------------------------------------

    def _start_log_tail(self, service: str) -> None:
        """Start tailing logs for the given service."""
        if self._orch_in_progress:
            return

        if self._log_task and not self._log_task.done():
            self._log_task.cancel()
        if self._log_process and self._log_process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                self._log_process.terminate()

        log_view = self.query_one("#log-view", RichLog)
        log_view.clear()
        label = self._config.service_labels.get(service, service)
        log_view.write(Text(f"--- Tailing {label} ---", style="dim italic"))

        self._log_task = asyncio.create_task(self._tail_logs(service))

    def _compose_file_for_service(self, service: str) -> str:
        """Find which compose file manages this service."""
        out = _run([*get_compose_cmd(self._compose_file), "ps", "--format", "json", service], timeout=5)
        if out.strip():
            return self._compose_file
        other = get_compose_file(self._config, not self._prod)
        other_path = Path(other)
        if other_path.exists():
            out = _run([*get_compose_cmd(other), "ps", "--format", "json", service], timeout=5)
            if out.strip():
                return other
        return self._compose_file

    async def _tail_logs(self, service: str) -> None:
        """Async task to tail docker compose logs or a log file."""
        if service.startswith("file:"):
            await self._tail_file(service.removeprefix("file:"))
        else:
            await self._tail_docker(service)

    async def _tail_docker(self, service: str) -> None:
        """Tail logs from a Docker compose service."""
        compose_file = self._compose_file_for_service(service)
        cmd = [*get_compose_cmd(compose_file), "logs", "-f", "--tail", "200", service]
        try:
            self._log_process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.STDOUT,
                cwd=PROJECT_ROOT,
            )
            log_view = self.query_one("#log-view", RichLog)

            while True:
                if self._log_process.stdout is None:
                    break
                line = await self._log_process.stdout.readline()
                if not line:
                    break
                text = line.decode("utf-8", errors="replace").rstrip()
                if text:
                    log_view.write(text)

        except asyncio.CancelledError:
            if self._log_process and self._log_process.returncode is None:
                try:
                    self._log_process.terminate()
                    await asyncio.wait_for(self._log_process.wait(), timeout=5)
                except (ProcessLookupError, TimeoutError):
                    pass
        except Exception as e:
            log_view = self.query_one("#log-view", RichLog)
            log_view.write(Text(f"Error: {e}", style="red"))

    async def _tail_file(self, name: str) -> None:
        """Tail a log file, similar to `tail -f`."""
        # Check orchestration log specially
        if name == "orchestration":
            path = self._config.logs_dir / "orchestration.log"
        else:
            path = self._config.log_files.get(name)
        log_view = self.query_one("#log-view", RichLog)
        if not path or not path.exists():
            log_view.write(Text(f"Log file not found: {name}", style="red"))
            log_view.write(Text("Start the service to create the log file.", style="dim"))
            return

        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
                for line in lines[-200:]:
                    text = line.rstrip()
                    if text:
                        log_view.write(text)

                while True:
                    line = f.readline()
                    if line:
                        text = line.rstrip()
                        if text:
                            log_view.write(text)
                    else:
                        await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            pass
        except Exception as e:
            log_view.write(Text(f"Error reading log: {e}", style="red"))

    @on(Select.Changed, "#service-select")
    def on_service_changed(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            self._start_log_tail(str(event.value))

    @on(Select.Changed, "#ref-select")
    def on_ref_select_changed(self, event: Select.Changed) -> None:
        if event.value is not Select.BLANK:
            ref = str(event.value)
            current = get_current_ref()
            if ref != current:
                self._do_checkout(ref)

    # -- Actions -----------------------------------------------------------

    def _update_action_visibility(self) -> None:
        """Show/hide action buttons based on aggregate state of checked services."""
        panel = self.query_one("#service-panel", ServicePanel)
        btn_restart = self.query_one("#btn-restart", Button)
        btn_stop = self.query_one("#btn-stop", Button)
        btn_start = self.query_one("#btn-start", Button)

        checked = self._get_checked_services()
        if not checked:
            btn_restart.add_class("hidden")
            btn_stop.add_class("hidden")
            btn_start.add_class("hidden")
            return

        all_running = all(
            panel.get_service_status(svc) in ("healthy", "running")
            for svc in checked
        )
        all_stopped = all(
            panel.get_service_status(svc) not in ("healthy", "running", "starting", "restarting")
            for svc in checked
        )

        if all_stopped:
            btn_restart.add_class("hidden")
            btn_stop.add_class("hidden")
            btn_start.remove_class("hidden")
        elif all_running:
            btn_restart.remove_class("hidden")
            btn_stop.remove_class("hidden")
            btn_start.add_class("hidden")
        else:
            btn_restart.remove_class("hidden")
            btn_stop.remove_class("hidden")
            btn_start.remove_class("hidden")

    @on(Select.Changed, "#selection-mode")
    def on_selection_mode_changed(self, event: Select.Changed) -> None:
        """Apply service selection based on dropdown choice, then reset."""
        if event.value is Select.BLANK:
            return

        mode = event.value
        panel = self.query_one("#service-panel", ServicePanel)

        # Determine which services to check
        to_check: set[str] = set()
        if mode == "all":
            to_check = set(self._config.service_order)
        elif mode == "changed":
            to_check = self._affected_services
        elif mode == "stopped":
            to_check = {
                svc for svc in self._config.service_order
                if panel.get_service_status(svc) not in ("healthy", "running")
            }
        elif mode == "running":
            to_check = {
                svc for svc in self._config.service_order
                if panel.get_service_status(svc) in ("healthy", "running")
            }
        # "none" leaves to_check empty

        for svc in self._config.service_order:
            self.query_one(f"#chk-{svc}", Checkbox).value = svc in to_check

        # Reset dropdown to blank
        self.query_one("#selection-mode", Select).value = Select.BLANK
        self._update_action_visibility()

    @on(Checkbox.Changed)
    def on_checkbox_changed(self, event: Checkbox.Changed) -> None:
        self._update_action_visibility()

        # Auto-switch log viewer when a service checkbox is clicked
        if event.checkbox.id and event.checkbox.id.startswith("chk-"):
            service = event.checkbox.id.removeprefix("chk-")
            select = self.query_one("#service-select", Select)
            for _label, value in self._get_service_options():
                if value == service:
                    select.value = service
                    break

    @on(Button.Pressed, "#btn-git-pull")
    def on_git_pull_pressed(self) -> None:
        self._do_git_pull()

    @on(Button.Pressed, "#btn-restart")
    def on_restart_pressed(self) -> None:
        self._do_service_action("restart")

    @on(Button.Pressed, "#btn-stop")
    def on_stop_pressed(self) -> None:
        self._do_service_action("stop")

    @on(Button.Pressed, "#btn-start")
    def on_start_pressed(self) -> None:
        self._do_service_action("start")

    @on(Button.Pressed, "#btn-reload")
    def on_reload_pressed(self) -> None:
        """Re-exec the dashboard to pick up script changes."""
        os.execv(sys.executable, [sys.executable, *sys.argv])

    def _show_reload_button(self) -> None:
        self.query_one("#btn-reload", Button).remove_class("hidden")

    def action_focus_logs(self) -> None:
        self.query_one("#service-select", Select).focus()

    def action_git_pull(self) -> None:
        self._do_git_pull()

    def action_refresh(self) -> None:
        self._refresh_status()
        log_view = self.query_one("#log-view", RichLog)
        log_view.write(Text("--- Status refreshed ---", style="dim italic"))

    def action_stop(self) -> None:
        self._do_service_action("stop")

    def action_start(self) -> None:
        self._do_service_action("start")

    def action_restart(self) -> None:
        self._do_service_action("restart")

    def action_next_theme(self) -> None:
        themes = sorted(self.available_themes)
        if not themes:
            return
        try:
            idx = themes.index(self.theme)
            next_idx = (idx + 1) % len(themes)
        except ValueError:
            next_idx = 0
        self.theme = themes[next_idx]
        self._config.save_theme(self.theme)
        self.notify(f"Theme: {self.theme}")

    def _switch_to_orchestration(self) -> None:
        """Switch the dropdown to the orchestration log and start tailing it."""
        select = self.query_one("#service-select", Select)
        orch_path = self._config.logs_dir / "orchestration.log"
        orch_path.parent.mkdir(parents=True, exist_ok=True)
        orch_path.touch(exist_ok=True)
        options = self._get_service_options()
        select.set_options(options)
        select.value = "file:orchestration"

    def _write_orch(self, log_view: RichLog, log_file, text: str | Text) -> None:
        """Write a line to both the log view and orchestration log file."""
        log_view.write(text)
        plain = text.plain if isinstance(text, Text) else text
        log_file.write(plain + "\n")
        log_file.flush()

    def _run_streaming(
        self,
        cmd: list[str],
        log_view: RichLog,
        log_file,
        timeout: int = 300,
    ) -> int:
        """Run a command, streaming stdout+stderr line-by-line to log view and file."""
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=PROJECT_ROOT,
        )
        try:
            assert proc.stdout is not None
            for line in proc.stdout:
                text = line.rstrip()
                if text:
                    self._write_orch(log_view, log_file, text)
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
            raise
        return proc.returncode

    @work(thread=True)
    def _fetch_and_refresh_refs(self) -> None:
        _run(["git", "fetch", "--prune"], timeout=30)
        self.call_from_thread(self._refresh_ref_select)

    def _refresh_ref_select(self) -> None:
        select = self.query_one("#ref-select", Select)
        refs = get_git_refs()
        current = get_current_ref()
        with select.prevent(Select.Changed):
            select.set_options(refs)
            for _label, value in refs:
                if value == current:
                    select.value = current
                    return
            if refs:
                select.value = refs[0][1]

    @work(exclusive=True, thread=True)
    def _do_git_pull(self) -> None:
        """Pull latest code without restarting services."""
        log_view = self.query_one("#log-view", RichLog)

        if self._log_task and not self._log_task.done():
            self._log_task.cancel()

        log_view.clear()

        self._config.logs_dir.mkdir(parents=True, exist_ok=True)
        orch_path = self._config.logs_dir / "orchestration.log"

        self.query_one("#btn-git-pull", Button).disabled = True
        self._orch_in_progress = True
        self.call_from_thread(self._switch_to_orchestration)

        try:
            with open(orch_path, "a", encoding="utf-8") as orch:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._write_orch(log_view, orch, Text(
                    f"=== Git Pull ({timestamp}) ===", style="bold yellow",
                ))

                old_sha = _run(["git", "rev-parse", "HEAD"])

                self._write_orch(log_view, orch, Text("\n--- git pull ---", style="bold"))
                rc = self._run_streaming(["git", "pull"], log_view, orch, timeout=60)

                if rc != 0:
                    self._write_orch(log_view, orch, Text("git pull failed!", style="red bold"))
                    return

                new_sha = _run(["git", "rev-parse", "HEAD"])

                if old_sha == new_sha:
                    self._write_orch(log_view, orch, Text(
                        "\nAlready up to date.", style="green bold",
                    ))
                else:
                    changed_files = get_changed_files(old_sha, new_sha)
                    self._write_orch(log_view, orch, Text(
                        f"\nPulled {len(changed_files)} changed file(s).",
                        style="green bold",
                    ))

                    affected = detect_affected_services(self._config, changed_files)
                    if affected:
                        self._affected_services = affected
                        svc_list = ", ".join(sorted(affected))
                        self._write_orch(log_view, orch, Text(
                            f"Affected services: {svc_list}",
                            style="cyan",
                        ))
                        # Auto-select affected services
                        def _select_affected() -> None:
                            for svc in affected:
                                try:
                                    self.query_one(f"#chk-{svc}", Checkbox).value = True
                                except Exception:
                                    pass
                            self._update_action_visibility()
                        self.call_from_thread(_select_affected)

                    # Check if dashboard script was updated
                    script_rel = _get_script_relative_path()
                    if script_rel and any(f.startswith(script_rel) for f in changed_files):
                        self._write_orch(log_view, orch, Text(
                            "\nDashboard script was updated.",
                            style="yellow bold",
                        ))
                        self.call_from_thread(self._show_reload_button)

                    if WEBHOOK_SIGNAL_FILE.exists():
                        with contextlib.suppress(OSError):
                            WEBHOOK_SIGNAL_FILE.unlink()

        except subprocess.TimeoutExpired:
            log_view.write(Text("git pull timed out!", style="red bold"))
        except Exception as e:
            log_view.write(Text(f"Error: {e}", style="red"))
        finally:
            self.query_one("#btn-git-pull", Button).disabled = False
            self._git_info = get_git_info()
            env_mode = "prod" if self._prod else "dev"
            self.sub_title = f"{env_mode} | {self._git_info}"
            self._orch_in_progress = False
            self.call_from_thread(self._refresh_status)
            self.call_from_thread(self._refresh_ref_select)

    @work(exclusive=True, thread=True)
    def _do_checkout(self, ref: str) -> None:
        """Checkout a git ref and update the subtitle."""
        log_view = self.query_one("#log-view", RichLog)

        if self._log_task and not self._log_task.done():
            self._log_task.cancel()

        log_view.clear()

        self._config.logs_dir.mkdir(parents=True, exist_ok=True)
        orch_path = self._config.logs_dir / "orchestration.log"

        self._orch_in_progress = True
        self.call_from_thread(self._switch_to_orchestration)

        try:
            with open(orch_path, "a", encoding="utf-8") as orch:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._write_orch(log_view, orch, Text(f"=== Checkout ({timestamp}) ===", style="bold yellow"))

                self._write_orch(log_view, orch, Text(f"\n--- git checkout {ref} ---", style="bold"))
                rc = self._run_streaming(["git", "checkout", ref], log_view, orch, timeout=30)

                if rc == 0:
                    self._write_orch(log_view, orch, Text(f"\nChecked out {ref}", style="green bold"))
                    self._git_info = get_git_info()
                    mode = "prod" if self._prod else "dev"
                    self.sub_title = f"{mode} | {self._git_info}"
                else:
                    self._write_orch(log_view, orch, Text("\nCheckout failed!", style="red bold"))

        except subprocess.TimeoutExpired:
            log_view.write(Text("Checkout timed out!", style="red bold"))
        except Exception as e:
            log_view.write(Text(f"Error: {e}", style="red"))
        finally:
            self._orch_in_progress = False
            self.call_from_thread(self._refresh_ref_select)

    def _get_checked_services(self) -> set[str]:
        checked: set[str] = set()
        for svc in self._config.service_order:
            chk = self.query_one(f"#chk-{svc}", Checkbox)
            if chk.value:
                checked.add(svc)
        return checked

    def _disable_action_buttons(self, disable: bool = True) -> None:
        """Disable or enable all action buttons."""
        for btn_id in ("#btn-stop", "#btn-start", "#btn-restart"):
            self.query_one(btn_id, Button).disabled = disable

    @work(exclusive=True, thread=True)
    def _do_service_action(self, action: str) -> None:
        """Execute stop/start/restart on checked services.

        Args:
            action: One of "stop", "start", "restart".
        """
        log_view = self.query_one("#log-view", RichLog)
        target_services = self._get_checked_services()

        if not target_services:
            return

        if self._log_task and not self._log_task.done():
            self._log_task.cancel()

        log_view.clear()

        self._config.logs_dir.mkdir(parents=True, exist_ok=True)
        orch_path = self._config.logs_dir / "orchestration.log"

        self._disable_action_buttons(True)
        self._orch_in_progress = True
        self.call_from_thread(self._switch_to_orchestration)

        try:
            with open(orch_path, "a", encoding="utf-8") as orch:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                svc_list = ", ".join(sorted(target_services))
                self._write_orch(log_view, orch, Text(
                    f"=== {action.title()} [{svc_list}] ({timestamp}) ===",
                    style="bold yellow",
                ))

                if action == "stop":
                    # Stop all selected services
                    all_targets = sorted(target_services)
                    svc_str = " ".join(all_targets)
                    self._write_orch(log_view, orch, Text(
                        f"\n--- docker compose stop {svc_str} ---",
                        style="bold",
                    ))
                    cmd = [*get_compose_cmd(self._compose_file), "stop", *all_targets]
                    rc = self._run_streaming(cmd, log_view, orch, timeout=120)
                    if rc != 0:
                        self._write_orch(log_view, orch, Text("Stop failed!", style="red bold"))
                        return
                    self._write_orch(log_view, orch, Text("\nStopped.", style="green bold"))

                elif action == "start":
                    # Start infra first, then app services
                    infra_targets = sorted(target_services & self._config.infra_service_set)
                    if infra_targets:
                        svc_str = " ".join(infra_targets)
                        self._write_orch(log_view, orch, Text(
                            f"\n--- docker compose up -d {svc_str} ---",
                            style="bold",
                        ))
                        cmd = [*get_compose_cmd(self._compose_file), "up", "-d", *infra_targets]
                        rc = self._run_streaming(cmd, log_view, orch, timeout=120)
                        if rc != 0:
                            self._write_orch(log_view, orch, Text("Start failed!", style="red bold"))
                            return

                    app_targets = sorted(target_services & self._config.app_services)
                    if app_targets:
                        svc_str = " ".join(app_targets)
                        self._write_orch(log_view, orch, Text(
                            f"\n--- docker compose up -d {svc_str} ---",
                            style="bold",
                        ))
                        cmd = [*get_compose_cmd(self._compose_file), "up", "-d", *app_targets]
                        rc = self._run_streaming(cmd, log_view, orch, timeout=120)
                        if rc != 0:
                            self._write_orch(log_view, orch, Text("Start failed!", style="red bold"))
                            return

                    self._write_orch(log_view, orch, Text("\nStarted.", style="green bold"))

                elif action == "restart":
                    # Restart infra first (plain restart), then rebuild app services
                    infra_targets = sorted(target_services & self._config.infra_service_set)
                    if infra_targets:
                        svc_str = " ".join(infra_targets)
                        self._write_orch(log_view, orch, Text(
                            f"\n--- docker compose restart {svc_str} ---",
                            style="bold",
                        ))
                        cmd = [*get_compose_cmd(self._compose_file), "restart", *infra_targets]
                        rc = self._run_streaming(cmd, log_view, orch, timeout=120)
                        if rc != 0:
                            self._write_orch(log_view, orch, Text("Restart failed!", style="red bold"))
                            return

                    app_targets = sorted(target_services & self._config.app_services)
                    if app_targets:
                        svc_str = " ".join(app_targets)
                        self._write_orch(log_view, orch, Text(
                            f"\n--- docker compose up -d --build {svc_str} ---",
                            style="bold",
                        ))
                        cmd = [*get_compose_cmd(self._compose_file), "up", "-d", "--build", *app_targets]
                        rc = self._run_streaming(cmd, log_view, orch, timeout=300)
                        if rc != 0:
                            self._write_orch(log_view, orch, Text("Restart failed!", style="red bold"))
                            return

                    self._write_orch(log_view, orch, Text("\nRestart complete!", style="green bold"))

        except subprocess.TimeoutExpired:
            log_view.write(Text("Command timed out!", style="red bold"))
        except Exception as e:
            log_view.write(Text(f"Error: {e}", style="red"))
        finally:
            self._affected_services -= target_services
            self._disable_action_buttons(False)
            self._orch_in_progress = False
            self.call_from_thread(self._refresh_status)

    async def on_unmount(self) -> None:
        """Clean up on exit."""
        if self._log_task and not self._log_task.done():
            self._log_task.cancel()
        if self._log_process and self._log_process.returncode is None:
            with contextlib.suppress(ProcessLookupError):
                self._log_process.terminate()


# ---------------------------------------------------------------------------
# Helpers (script-relative)
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


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def _self_update() -> None:
    """Pull latest code and re-exec if this script changed."""
    if _is_installed_package():
        return

    script = Path(__file__).resolve()
    old_mtime = script.stat().st_mtime

    # Pull the StackTUI repo if it differs from the managed project
    stacktui_repo = _get_stacktui_repo_root()
    if stacktui_repo and stacktui_repo != PROJECT_ROOT:
        result = subprocess.run(
            ["git", "pull", "--ff-only"],
            capture_output=True, text=True, timeout=30, cwd=stacktui_repo,
        )
        if result.returncode != 0:
            print(f"StackTUI pull failed: {result.stderr.strip()}")

        if script.stat().st_mtime != old_mtime:
            print("StackTUI updated — restarting...")
            os.execv(sys.executable, [sys.executable, *sys.argv])

    # Pull the managed project
    result = subprocess.run(
        ["git", "pull", "--ff-only"],
        capture_output=True, text=True, timeout=30, cwd=PROJECT_ROOT,
    )
    if result.returncode != 0:
        print(f"git pull failed: {result.stderr.strip()}")
        return

    if result.stdout.strip() == "Already up to date.":
        return

    if script.stat().st_mtime != old_mtime:
        print("Dashboard updated — restarting...")
        os.execv(sys.executable, [sys.executable, *sys.argv])


def main() -> None:
    parser = argparse.ArgumentParser(description="StackTUI — Docker Compose Dashboard")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--prod", action="store_true", help="Force production mode")
    group.add_argument("--dev", action="store_true", help="Force development mode")
    parser.add_argument("--no-update", action="store_true", help="Skip self-update on startup")
    parser.add_argument("--config", type=str, default=None, help="Path to dashboard.toml config file")
    args = parser.parse_args()

    if not args.no_update:
        _self_update()

    config = find_config(args.config)

    # Set the global webhook signal file path
    global WEBHOOK_SIGNAL_FILE
    WEBHOOK_SIGNAL_FILE = config.logs_dir / "github_push.json"

    if args.prod:
        prod: bool | None = True
    elif args.dev:
        prod = False
    else:
        prod = None

    app = Dashboard(config=config, prod=prod)
    app.run()


if __name__ == "__main__":
    main()
