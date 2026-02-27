"""Main Dashboard application class for StackTUI."""

from __future__ import annotations

import asyncio
import contextlib
import os
import subprocess
import sys
from datetime import datetime
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

from .config import PROJECT_ROOT, DashboardConfig
from .helpers import (
    WEBHOOK_SIGNAL_FILE,
    _check_stacktui_updates,
    _get_script_relative_path,
    _get_stacktui_repo_root,
    _run,
    check_webhook_signal,
    detect_affected_services,
    detect_native_processes,
    detect_prod_mode,
    get_base_url,
    get_changed_files,
    get_compose_cmd,
    get_compose_file,
    get_current_ref,
    get_data_freshness,
    get_git_info,
    get_git_refs,
    get_git_status_summary,
    parse_all_containers,
    parse_services,
)
from .widgets import (
    LinksPanel,
    ServicePanel,
    UpdateBanner,
    WebhookBanner,
)


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

    #btn-rebuild {
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

    #btn-rebuild.hidden {
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
        Binding("b", "rebuild", "Rebuild"),
        Binding("l", "focus_logs", "Logs"),
        Binding("T", "next_theme", "Theme"),
    ]

    def __init__(self, config: DashboardConfig, prod: bool | None = None) -> None:
        super().__init__()
        self._config = config
        self.title = f"{config.project_name}"
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
        yield Header(show_clock=True)

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
                yield Button("Rebuild", id="btn-rebuild", variant="primary", classes="hidden")
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

    def _build_subtitle(self) -> str:
        """Build header subtitle: '{mode} | {branch}@{sha} | {status}'."""
        mode = "prod" if self._prod else "dev"
        subtitle = f"{mode} | {self._git_info}"
        status = get_git_status_summary()
        if status:
            subtitle += f" | {status}"
        return subtitle

    def on_mount(self) -> None:
        if self._config.theme_name in self.available_themes:
            self.theme = self._config.theme_name

        self.sub_title = self._build_subtitle()

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
        option_values = {v for _l, v in options}
        # Prefer saved user preference (if still available)
        if self._config.last_selected_log and self._config.last_selected_log in option_values:
            return self._config.last_selected_log
        # Fall back to first primary service
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

        self._git_info = get_git_info()
        self.sub_title = self._build_subtitle()

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
            service = str(event.value)
            self._start_log_tail(service)
            self._config.save_selected_log(service)

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
        btn_restart = self.query_one("#btn-restart", Button)
        btn_rebuild = self.query_one("#btn-rebuild", Button)
        btn_stop = self.query_one("#btn-stop", Button)
        btn_start = self.query_one("#btn-start", Button)

        if self._orch_in_progress:
            btn_restart.add_class("hidden")
            btn_rebuild.add_class("hidden")
            btn_stop.add_class("hidden")
            btn_start.add_class("hidden")
            return

        panel = self.query_one("#service-panel", ServicePanel)

        checked = self._get_checked_services()
        if not checked:
            btn_restart.add_class("hidden")
            btn_rebuild.add_class("hidden")
            btn_stop.add_class("hidden")
            btn_start.add_class("hidden")
            return

        statuses = {svc: panel.get_service_status(svc) for svc in checked}
        any_transitional = any(s in ("starting", "restarting") for s in statuses.values())
        all_running = all(s in ("healthy", "running") for s in statuses.values())
        all_stopped = all(s not in ("healthy", "running", "starting", "restarting") for s in statuses.values())

        if any_transitional:
            # Services are still coming up — hide all action buttons
            btn_restart.add_class("hidden")
            btn_rebuild.add_class("hidden")
            btn_stop.add_class("hidden")
            btn_start.add_class("hidden")
        elif all_stopped:
            btn_restart.add_class("hidden")
            btn_rebuild.add_class("hidden")
            btn_stop.add_class("hidden")
            btn_start.remove_class("hidden")
        elif all_running:
            btn_restart.remove_class("hidden")
            btn_rebuild.remove_class("hidden")
            btn_stop.remove_class("hidden")
            btn_start.add_class("hidden")
        else:
            btn_restart.remove_class("hidden")
            btn_rebuild.remove_class("hidden")
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

    @on(Button.Pressed, "#btn-rebuild")
    def on_rebuild_pressed(self) -> None:
        self._do_service_action("rebuild")

    @on(Button.Pressed, "#btn-stop")
    def on_stop_pressed(self) -> None:
        self._do_service_action("stop")

    @on(Button.Pressed, "#btn-start")
    def on_start_pressed(self) -> None:
        self._do_service_action("start")

    @on(Button.Pressed, "#btn-update-restart")
    def on_update_restart_pressed(self) -> None:
        """Pull StackTUI updates and re-exec."""
        repo = _get_stacktui_repo_root()
        if repo and repo != PROJECT_ROOT:
            subprocess.run(
                ["git", "pull", "--ff-only"],
                capture_output=True, text=True, timeout=30, cwd=repo,
            )
        os.execv(sys.executable, [sys.executable, *sys.argv])

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

    def action_rebuild(self) -> None:
        self._do_service_action("rebuild")

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
                        # Auto-select only affected services (clear previous)
                        def _select_affected() -> None:
                            for cb in self.query(Checkbox):
                                svc_id = cb.id or ""
                                svc_name = svc_id.removeprefix("chk-")
                                cb.value = svc_name in affected
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
            self.sub_title = self._build_subtitle()
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
                    self.sub_title = self._build_subtitle()
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
        for btn_id in ("#btn-stop", "#btn-start", "#btn-restart", "#btn-rebuild"):
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

                elif action == "rebuild":
                    # Explicit build then recreate — works for any service
                    all_targets = sorted(target_services)
                    svc_str = " ".join(all_targets)
                    self._write_orch(log_view, orch, Text(
                        f"\n--- docker compose build {svc_str} ---",
                        style="bold",
                    ))
                    cmd = [*get_compose_cmd(self._compose_file), "build", *all_targets]
                    rc = self._run_streaming(cmd, log_view, orch, timeout=300)
                    if rc != 0:
                        self._write_orch(log_view, orch, Text("Build failed!", style="red bold"))
                        return

                    self._write_orch(log_view, orch, Text(
                        f"\n--- docker compose up -d {svc_str} ---",
                        style="bold",
                    ))
                    cmd = [*get_compose_cmd(self._compose_file), "up", "-d", *all_targets]
                    rc = self._run_streaming(cmd, log_view, orch, timeout=120)
                    if rc != 0:
                        self._write_orch(log_view, orch, Text("Recreate failed!", style="red bold"))
                        return

                    self._write_orch(log_view, orch, Text("\nRebuild complete!", style="green bold"))

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
