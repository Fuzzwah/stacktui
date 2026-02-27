## Context

The ServicePanel currently displays each service as a checkbox + label + colored status dot/text (e.g., "● healthy"). The status data comes from `parse_services()` which calls `docker compose ps --format json -a` and parses each JSON line into a `ServiceInfo` object. The JSON output includes a `Status` field (e.g., "Up 3 days") and/or a `CreatedAt` timestamp, but neither is currently extracted.

The `update_services()` method on `ServicePanel` iterates `service_order`, looks up each service in the parsed map, and builds a `Text()` line with the status dot and text. This is where uptime display will be appended.

## Goals / Non-Goals

**Goals:**
- Extract uptime data from the existing `docker compose ps` JSON output (no additional Docker commands)
- Format uptime as compact human-readable text (e.g., "3d 4h", "23m")
- Display uptime inline in each service row, visually subordinate to the status indicator
- Update uptime on every 10-second refresh cycle

**Non-Goals:**
- Historical uptime tracking or persistence across dashboard sessions
- Uptime alerting or threshold-based warnings (could be a future enhancement)
- Uptime for native processes (pgrep-detected services have no Docker container)

## Decisions

### Decision 1: Use `Status` field parsing over `CreatedAt` timestamp

The `docker compose ps --format json` output includes both a `Status` string (e.g., "Up 3 hours", "Up 2 days") and a `CreatedAt` ISO timestamp.

**Choice**: Parse the `Status` field for the duration text.

**Rationale**: The `Status` field is what Docker itself computes and displays — it accounts for restarts (resets on restart), while `CreatedAt` is the container creation time which may not reflect the last start. The Status string is consistent across Docker Compose versions and already human-oriented.

**Alternative considered**: Computing from `CreatedAt` timestamp via `datetime` math. This would give precise control over formatting but would show time since creation, not time since last start, which is less useful for detecting restarts.

### Decision 2: Parse duration from Status string

Docker's Status field uses formats like "Up 3 hours", "Up About a minute", "Up 2 days". We'll parse this into seconds and then format it ourselves for consistency.

**Approach**: Regex extraction from the Status string to pull the numeric duration, then reformat using our own `format_uptime()` function for compact display ("3d 4h" instead of Docker's "Up 3 days").

**Fallback**: If parsing fails (unexpected format), store `None` and display nothing — graceful degradation, no crashes.

### Decision 3: Add `uptime` field to `ServiceInfo`

Add an `uptime_seconds: int | None` field to the `ServiceInfo` class. Populated during `parse_services()` from the Status field. `None` for stopped/missing containers.

Add a `uptime_text` property that calls `format_uptime()` for display.

### Decision 4: Uptime display position and style

Append uptime to the existing status `Text()` line in `update_services()`:

```
● healthy  3d 4h
● running  23m
—
```

Use `dim` style for the uptime text so it's visible but visually secondary to the status dot and text.

## Risks / Trade-offs

- **Status string format changes across Docker versions** → Mitigation: Use a permissive regex with fallback to `None`; dashboard still works, just without uptime display.
- **Slightly wider service rows** → Mitigation: Uptime text is short (max ~7 chars like "14d 2h") and dimmed, minimal visual impact.
- **No uptime for native processes** → Acceptable: native processes are dev-mode only and have no Docker container to query. Uptime shows as blank for these, consistent with the "no container" case.
