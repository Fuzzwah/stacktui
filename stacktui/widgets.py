"""Textual widget classes for the StackTUI dashboard."""

from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Checkbox, Static

from .config import DashboardConfig
from .helpers import ServiceInfo


# ---------------------------------------------------------------------------
# Widgets
# ---------------------------------------------------------------------------


class UpdateBanner(Horizontal):
    """Notification banner shown when StackTUI has upstream updates available."""

    DEFAULT_CSS = """
    UpdateBanner {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
        background: $primary-darken-2;
        color: $text;
        display: none;
        align: left middle;
    }
    UpdateBanner.visible {
        display: block;
    }
    UpdateBanner Static {
        width: 1fr;
        content-align: left middle;
    }
    UpdateBanner Button {
        min-width: 20;
        margin-left: 1;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static("", id="update-banner-text")
        yield Button("Restart to Update", id="btn-update-restart", variant="warning")

    def show_update(self, count: int) -> None:
        """Update banner with commit count and make it visible."""
        line = Text()
        line.append(f" StackTUI update available ", style="bold")
        line.append(f"({count} commit{'s' if count != 1 else ''} behind)", style="")
        self.query_one("#update-banner-text", Static).update(line)
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
                if info.uptime_text:
                    line.append(f"  {info.uptime_text}", style="dim")
                if info.image_tag and svc in self._config.infra_service_set:
                    line.append(f"  :{info.image_tag}", style="dim")
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
