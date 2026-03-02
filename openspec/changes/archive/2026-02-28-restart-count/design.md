## Context

The ServicePanel currently shows colored status dots, uptime, image tags, and error counts per service. The existing `parse_services()` queries `docker compose ps --format json` which returns container metadata — but RestartCount is not included in the compose ps output. A separate `docker inspect` call is needed per container.

The spec at `openspec/specs/restart-count/spec.md` defines: query restart counts, display when > 0, color escalation (yellow 1-4, red 5+), auto-select at 5+.

## Goals / Non-Goals

**Goals:**
- Show restart count indicators next to service status in the service panel
- Highlight restart-looping services (5+ restarts) with red styling and auto-selection
- Zero-restart services show no indicator (no visual noise)

**Non-Goals:**
- Historical restart tracking or alerting
- Restart count persistence across dashboard restarts
- Configurable thresholds (hardcoded at 5 for now)

## Decisions

### 1. Query via docker inspect per container

**Decision**: After `parse_services()` builds the service list, query `docker inspect --format '{{.RestartCount}}' <container_name>` for each service's container.

**Rationale**: `docker compose ps --format json` does not include RestartCount. Docker inspect is the standard way to get this. One call per container is acceptable for a typical 3-8 service stack.

**Alternatives considered**:
- Batch all containers in one `docker inspect` call — possible but adds JSON parsing complexity and the service list is already iterated
- Parse from `docker ps --format` — RestartCount not available in `docker ps` format either

### 2. Add restart_count to ServiceInfo

**Decision**: Add `restart_count: int` field to `ServiceInfo.__init__()`, default 0. Query it in `parse_services()` after building the service list.

**Rationale**: Follows the existing pattern of uptime_seconds and image being populated during parse_services(). Keeps ServiceInfo as the single data carrier for all per-service status data.

### 3. Badge format and placement

**Decision**: Append `" ↻N"` badge after existing status indicators (uptime, image tag, error count). Yellow for 1-4, red for 5+. Only shown when count > 0.

**Rationale**: Consistent with the error count badge pattern. The ↻ symbol clearly communicates "restart" and is compact. Placed after other badges to maintain reading order.

### 4. Auto-select at 5+ restarts

**Decision**: In `ServicePanel.update_services()`, treat services with restart_count >= 5 like unhealthy services — add them to the auto-check set.

**Rationale**: A container with 5+ restarts is likely in a crash loop and needs attention. This matches the spec's requirement and the existing auto-select behavior for unhealthy services.

## Risks / Trade-offs

- **[Performance] N docker inspect calls per refresh** → Acceptable for typical stack sizes (3-8 services). Each call is fast (~50ms).
- **[Counter reset] Docker resets RestartCount on container recreation** → This is actually desired behavior per the spec: manual restart via dashboard recreates the container, clearing the count.
