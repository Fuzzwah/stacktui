## Context

The dashboard (`stacktui/dashboard.py`) currently monitors service health via `docker compose ps` and `docker ps`, displaying colored status dots in the `ServicePanel`. A 10-second refresh cycle (`_refresh_status()`) polls Docker state. There is no resource usage visibility — users must run `docker stats` separately.

The existing `resource-usage` spec defines requirements for CPU/memory display per service. This design covers how to integrate that into the current architecture.

## Goals / Non-Goals

**Goals:**
- Display per-service CPU% and memory usage in the ServicePanel alongside existing status indicators
- Collect stats with a single `docker stats --no-stream --format json` call per refresh cycle
- Warn visually when resource usage is high (>80% CPU or memory limit)
- Gracefully handle failures without disrupting the dashboard

**Non-Goals:**
- Historical resource usage graphs or trends
- Resource limits configuration from the TUI
- Per-process resource tracking within containers
- Alerting or notification system for resource thresholds

## Decisions

### Decision 1: Single `docker stats` call per refresh cycle

**Choice**: Call `docker stats --no-stream --format json` once per refresh, parsing all containers from the output.

**Rationale**: `docker stats --no-stream` returns a point-in-time snapshot for all running containers in a single call. This mirrors the existing pattern of `docker compose ps` — one call, parse all results. No need for per-container queries.

**Alternative considered**: Running `docker stats` as a persistent stream and reading values. Rejected because it adds complexity (managing a long-running subprocess) and the 10-second refresh interval is sufficient for resource monitoring.

### Decision 2: Run stats collection in the existing `_refresh_status()` method

**Choice**: Add `get_resource_stats()` call inside `_refresh_status()`, passing the results to `ServicePanel.update_services()`.

**Rationale**: Resource data is tightly coupled with service status display — both update on the same cycle, both feed into `ServicePanel`. Adding a separate timer would risk race conditions and complicate the code for no benefit.

### Decision 3: Match containers to services by name

**Choice**: Match `docker stats` output to services using the same container-name-to-service-name logic already in `parse_all_containers()`.

**Rationale**: `docker stats` output includes the container name. The existing name-stripping logic (remove project prefix and `-1` suffix) already maps container names to service names. Reusing this avoids duplication.

### Decision 4: Compact inline display format

**Choice**: Show resource usage as dimmed text after the status indicator: `"45% 256M"` format.

**Rationale**: The ServicePanel rows already show status + uptime + image tag. Resource info follows the same pattern — compact, dimmed, appended. Using "%" for CPU and "M"/"G" for memory is instantly recognizable and minimal.

### Decision 5: Parse memory from `docker stats` MiB value

**Choice**: Parse the `MemUsage` field from `docker stats` JSON output (e.g., "256MiB / 1GiB"), extract the current usage portion, and convert to a compact display format.

**Rationale**: Docker stats already provides human-readable memory values. We parse the current usage (before the `/`) and re-format for compactness (drop "iB" suffix, round to one decimal for GiB).

## Risks / Trade-offs

- **[Performance]** `docker stats --no-stream` takes ~1-2 seconds to complete → Run it alongside existing Docker queries in the same refresh cycle; the refresh interval (10s) provides ample headroom. If it proves slow, it could be moved to a separate timer with a longer interval.
- **[Stale data]** Stats are point-in-time snapshots, not averages → Acceptable for a dashboard overview; users who need precise data will use `docker stats` directly.
- **[Container matching]** Containers with non-standard naming won't match → Same limitation as existing service detection; consistent with the project's approach.
