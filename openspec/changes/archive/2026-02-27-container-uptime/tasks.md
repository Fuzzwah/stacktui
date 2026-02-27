## 1. Data Extraction

- [x] 1.1 Add `uptime_seconds: int | None = None` field to `ServiceInfo.__init__()` in `stacktui/dashboard.py`
- [x] 1.2 Add `_parse_uptime(status: str) -> int | None` helper function that extracts seconds from Docker Status strings (e.g., "Up 3 hours", "Up 2 days", "Up About a minute")
- [x] 1.3 Call `_parse_uptime()` in `parse_services()` to populate `ServiceInfo.uptime_seconds` from the `Status` JSON field

## 2. Duration Formatting

- [x] 2.1 Add `format_uptime(seconds: int) -> str` module-level helper that returns compact duration text (e.g., "3d 4h", "23m", "45s")
- [x] 2.2 Add `uptime_text` property to `ServiceInfo` that returns `format_uptime(self.uptime_seconds)` or empty string when `None`

## 3. ServicePanel Display

- [x] 3.1 Update `ServicePanel.update_services()` to append uptime text (dim style) after the status dot and text in each service row
- [x] 3.2 Skip uptime display for services with no container (the "—" case) and native processes

## 4. Verification

- [x] 4.1 Run the dashboard against the demo environment (`uv run stacktui --dev`) and confirm uptime appears next to running services
- [x] 4.2 Restart a service and confirm uptime resets to a small value on the next refresh
- [x] 4.3 Stop a service and confirm no uptime text appears for stopped services
