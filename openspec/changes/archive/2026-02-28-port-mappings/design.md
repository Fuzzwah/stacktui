## Context

The ServicePanel currently displays each service with a colored status dot, status text, optional uptime, optional image tag, and optional error count. Port information is not shown, requiring users to check `docker-compose.yml` or run `docker compose ps` manually.

The `docker compose ps --format json` output already includes a `Publishers` field containing an array of port mapping objects, e.g.:
```json
{"PublishedPort": 8000, "TargetPort": 80, "Protocol": "tcp"}
```

The `ServiceInfo` class and `parse_services()` function handle all Docker JSON parsing. The `update_services()` method in `ServicePanel` builds the `Text` line for each service row.

## Goals / Non-Goals

**Goals:**
- Extract host port mappings from existing Docker Compose JSON output
- Display ports compactly in the ServicePanel status line
- Keep port display unobtrusive (dimmed styling, after existing status info)
- Ports refresh automatically with the existing 10-second polling cycle

**Non-Goals:**
- Displaying container-side (target) ports — users care about which port to connect to on localhost
- Making ports clickable or interactive
- Showing UDP vs TCP protocol distinctions
- Port mapping for native processes (dev mode `pgrep`-detected services)

## Decisions

### 1. Store ports as a list of integers on ServiceInfo

**Decision**: Add a `ports: list[int]` field to `ServiceInfo` containing sorted, deduplicated published (host) ports.

**Rationale**: Only host ports matter for user connectivity. Storing as simple integers keeps the data model minimal. Sorting ensures consistent display order.

**Alternative considered**: Storing full `{host_port, container_port, protocol}` tuples — rejected as unnecessary complexity for the display-only use case.

### 2. Extract from Publishers field in parse_services()

**Decision**: Parse the `Publishers` JSON array in `parse_services()`, extracting `PublishedPort` values > 0.

**Rationale**: The data is already present in the `docker compose ps --format json` output — no additional Docker commands needed. `PublishedPort` of 0 indicates an exposed but unpublished port (EXPOSE without -p), which should be excluded.

### 3. Display format: `:PORT` after status info, dim style

**Decision**: Append port strings like `:8000` or `:80 :443` at the end of the status line in dimmed style, after all existing status elements (uptime, image tag, error count).

**Rationale**: Matches the existing dim-styled metadata pattern (uptime, image tags). Placing ports last avoids disrupting the primary status→uptime→errors reading flow. The colon prefix (`:8000`) is compact and universally understood as a port notation.

### 4. Handle duplicate ports when deduplicating services

**Decision**: When `parse_services()` deduplicates by service name (keeping highest-priority state), the ports from the winning container are used.

**Rationale**: Follows the existing deduplication pattern — the "winning" container's data is authoritative.

## Risks / Trade-offs

- **[Visual clutter]** → Mitigated by dim styling and only showing non-empty port lists. Services without published ports show nothing extra.
- **[Long port lists]** → Unlikely in practice (most services publish 1-2 ports). If a service publishes many ports, the line may wrap, but Textual handles this gracefully.
