## Context

The ServicePanel currently shows a colored status dot (healthy/running/stopped) and optional uptime per service. Users must manually tail logs via the dropdown to discover errors. The existing `_refresh_status()` loop already polls Docker every 10 seconds and calls `update_services()` — this is the natural integration point.

The spec at `openspec/specs/log-error-count/spec.md` already defines the full requirements: scanning `--tail=100`, error patterns, badge display with color escalation, and optional config.

## Goals / Non-Goals

**Goals:**
- Surface error counts in the service panel without requiring log tailing
- Keep it lightweight — no persistent state, no background processes beyond the existing refresh loop
- Make error patterns configurable for projects with non-standard log formats

**Non-Goals:**
- Real-time streaming error detection (that's log tailing territory)
- Historical error tracking or trending over time
- Error categorization or deduplication (just raw line counts)
- Notification/alerting on error thresholds

## Decisions

### 1. Scan at refresh time, not continuously

**Decision**: Run `docker compose logs --tail=100 <service>` for each running service during `_refresh_status()`, rather than maintaining persistent log watchers.

**Rationale**: The refresh loop already runs every 10 seconds. Scanning tail output is simple, stateless, and consistent with how freshness monitoring works. A persistent watcher would add complexity (managing subprocesses, aggregating counts) for minimal benefit — the tail window already captures recent errors.

**Alternatives considered**:
- Persistent log watchers per service — too complex, subprocess management burden
- Single `docker compose logs --tail=100` (all services at once) — harder to attribute lines to services reliably

### 2. New `get_error_counts()` module-level helper

**Decision**: Add a `get_error_counts()` function that takes the config, compose file, and list of running service names. Returns a `dict[str, int]` mapping service name to error count.

**Rationale**: Follows the existing pattern of module-level helpers (`parse_services()`, `get_data_freshness()`) called from `_refresh_status()`. Keeps the ServicePanel decoupled from Docker commands.

### 3. Badge appended to existing status line

**Decision**: Append the error badge to the `Text` object in `update_services()`, after the uptime text. Format: `"N err"` in yellow (< 20) or red (>= 20).

**Rationale**: Minimal layout disruption. The service row already uses `Text.append()` for status + uptime; one more append for the badge is clean. No new widgets or layout changes needed.

### 4. Config via `[logs]` section

**Decision**: Add `error_patterns` as an optional list under the existing `[logs]` config section. Store as `DashboardConfig.error_patterns: list[str]` with defaults `["ERROR", "CRITICAL", "FATAL", "PANIC"]`.

**Rationale**: Error scanning is log-related, so `[logs]` is the natural home. Keeps the config surface small — a single list of strings with sensible defaults.

## Risks / Trade-offs

- **[Performance] N subprocess calls per refresh** → Mitigated by `--tail=100` limit. For a typical 5-service stack, this adds ~5 short-lived subprocess calls every 10 seconds. Acceptable for a TUI dashboard.
- **[False positives] Pattern matching is line-based and naive** → Mitigated by case-insensitive matching of standard log level keywords. Custom patterns config provides an escape hatch for noisy projects.
- **[UI clutter] Badge on every service row** → Mitigated by only showing the badge when count > 0. Zero-error services show no badge.
