"""Configuration loading and data types for StackTUI."""

from __future__ import annotations

import sys
import tomllib
from dataclasses import dataclass, field
from pathlib import Path

import tomlkit

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path.cwd()
USER_PREFS_FILENAME = ".stacktui-user.toml"


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


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

    # Error detection patterns for log scanning
    error_patterns: list[str] = field(
        default_factory=lambda: ["ERROR", "CRITICAL", "FATAL", "PANIC"]
    )

    # Theme
    theme_name: str = "nord"

    # Last selected log service (persisted in user prefs)
    last_selected_log: str = ""

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
        if "error_patterns" in logs:
            config.error_patterns = logs["error_patterns"]

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
            user_log = user_data.get("logs", {}).get("selected", "")
            if user_log:
                config.last_selected_log = user_log

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

    def save_selected_log(self, service: str) -> None:
        """Save the selected log service to the per-user preferences file."""
        if self.user_prefs_path is None:
            return
        if self.user_prefs_path.exists():
            doc = tomlkit.parse(self.user_prefs_path.read_text())
        else:
            doc = tomlkit.document()
            doc.add(tomlkit.comment("Per-user StackTUI preferences (not committed to git)"))
            doc.add(tomlkit.nl())
        if "logs" not in doc:
            doc.add("logs", tomlkit.table())
        doc["logs"]["selected"] = service
        self.user_prefs_path.write_text(tomlkit.dumps(doc))
