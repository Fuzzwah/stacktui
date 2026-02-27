## Context

The ServicePanel currently displays each service as a checkbox + status line:
```
☐ Web App       ● healthy  3d 4h
☐ Redis         ● running
```

`parse_services()` already calls `docker compose ps --format json -a`, which returns an `Image` field per container. This data is available but not captured or displayed. The `ServiceInfo` class has no `image` field.

## Goals / Non-Goals

**Goals:**
- Display image tags (e.g., `:16.2`) next to infra service status in the ServicePanel
- Extract image data from existing `docker compose ps` output (no additional Docker commands)
- Cleanly handle edge cases: no tag, `latest` tag, long registry prefixes, locally-built images

**Non-Goals:**
- Comparing running versions against available updates (version drift detection)
- Showing image digest/SHA information
- Adding image version to log output or orchestration history
- Modifying the config format — this is purely additive display logic

## Decisions

**1. Data source: `docker compose ps --format json` Image field**

The JSON output from `docker compose ps` includes an `Image` field (e.g., `postgres:16.2`, `registry.example.com/org/redis:7.4-alpine`). This avoids any additional Docker API calls.

Alternative considered: `docker inspect --format '{{.Config.Image}}'` — requires a separate call per container, slower.

**2. Add `image` field to `ServiceInfo`**

Add a single `image: str` field to `ServiceInfo` containing the raw image string from Docker. Add an `image_tag` property that extracts just the tag portion (everything after the last `:`), returning empty string for locally-built images without tags.

Alternative considered: Storing parsed name/tag separately — unnecessary complexity since we only display the tag.

**3. Display tag after status text for infra services only**

Append the tag in dim style after the status/uptime text. For primary services (locally built), skip display when the tag is empty or not meaningful. The config already distinguishes primary vs infra services, so use that to control display.

Layout: `● healthy  3d 4h  :16.2`

Alternative considered: Showing tag after the service label (checkbox) — conflicts with checkbox label formatting in Textual and mixes static labels with dynamic data.

**4. Tag-only display with truncation**

Show only `:tag` (e.g., `:16.2-alpine`), not the full image path. This keeps the display compact. Registry prefixes like `registry.example.com/org/` add no value in this context.

## Risks / Trade-offs

- [Image field missing from JSON] → Fall back to empty string; tag simply not displayed. No error.
- [Tag-only display loses image name context] → Acceptable since the service label already identifies what's running. Full image name is available via `docker compose ps` if needed.
- [Slightly wider status line] → Tags are typically short (`:16.2`, `:7.4`). Dim styling minimizes visual impact.
