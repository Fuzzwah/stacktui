## Context

The dashboard supports theme cycling via `Shift+T` and loading a default theme from `[theme] name` in `dashboard.toml`. However, the selected theme is not saved — it resets on every restart. The config object (`DashboardConfig`) doesn't track which file it was loaded from, so there's no way to write back. Python's stdlib includes `tomllib` for reading TOML but has no TOML writer.

## Goals / Non-Goals

**Goals:**
- Persist theme selection to `dashboard.toml` when the user cycles themes
- Change the default theme to `nord` when no `[theme]` section exists
- Track the config file path on `DashboardConfig` for write-back

**Non-Goals:**
- Adding a TOML writing library dependency
- Making other config values writable at runtime
- Theme preview or theme browser UI

## Decisions

### 1. Text-based TOML write-back using regex

**Decision**: Use `re.sub()` on the raw TOML file text to update or insert the `[theme]` section.

**Rationale**: Python stdlib has no TOML writer. Adding a dependency (`tomlkit`, `tomli-w`) for a single key update is overkill. The `[theme]` section is simple (one key), making regex safe and predictable.

**Alternatives considered**:
- `tomlkit` library: Preserves formatting but adds a dependency for minimal benefit
- Rewrite entire file from config object: Would lose comments and formatting

**Approach**:
- If a `name = ...` line exists under `[theme]`, replace its value
- If `[theme]` section exists but no `name` key, append the key
- If no `[theme]` section exists, append the entire section to the file

### 2. Store config file path on DashboardConfig

**Decision**: Add a `config_path: Path | None` field to `DashboardConfig`, set during `load()`.

**Rationale**: The path is needed to write back. Storing it on the config object is the simplest approach — no global state or extra parameters needed.

### 3. Save method on DashboardConfig

**Decision**: Add a `save_theme(theme_name: str)` method to `DashboardConfig` that handles the TOML text manipulation.

**Rationale**: Keeps the file I/O logic co-located with the config class rather than in the UI layer.

## Risks / Trade-offs

- **[Risk] Regex could mismatch commented-out `[theme]` sections** → The regex anchors on `^\[theme\]` at line start, which matches standard TOML. Commented lines start with `#` and won't match.
- **[Risk] Concurrent writes if config is edited externally** → Acceptable for a single-user TUI. The write is atomic (read-modify-write in one operation).
- **[Trade-off] No TOML format validation on write** → We only touch one key, so the rest of the file is preserved exactly. Risk of corruption is minimal.
