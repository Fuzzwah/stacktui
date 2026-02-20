## Context

`DashboardConfig.save_theme()` currently uses regex (`re.subn`) to find and replace the theme name in the raw TOML text. The replacement strings use raw f-strings (`rf"..."`) with `\"`, which produces literal backslash-quote characters in the output — corrupting the TOML file and crashing the app on next startup.

## Goals / Non-Goals

**Goals:**
- Fix the TOML corruption bug in `save_theme()`
- Use a proper TOML library for config write-back so future config saves are safe

**Non-Goals:**
- Replacing `tomllib` for reading (stdlib is fine for read-only)
- Adding other config write-back operations (future work)
- Migrating existing corrupted config files on user machines

## Decisions

### Use `tomlkit` for TOML writing

**Choice**: `tomlkit` over `tomli_w` or manual string manipulation

**Rationale**: `tomlkit` preserves comments, formatting, and whitespace when round-tripping TOML files. This matters because users hand-edit their `dashboard.toml` and would lose comments/formatting with a naive write library. `tomli_w` writes valid TOML but doesn't preserve formatting.

**Implementation**: Parse with `tomlkit.parse()`, mutate the document object, write with `tomlkit.dumps()`. Four lines replacing ~20 lines of regex.

## Risks / Trade-offs

- **[New dependency]** → `tomlkit` is well-maintained, pure Python, no transitive dependencies. Acceptable trade-off for correctness.
- **[Two TOML parsers]** → `tomllib` (read) + `tomlkit` (write) coexist. Could consolidate to `tomlkit` for both, but `tomllib` is stdlib and works fine for reading. No action needed now.
