## Context

Orchestration operations (stop, start, restart, rebuild) log to `logs/orchestration.log` with structured headers:
```
=== Restart [webapp, worker] (2026-02-27 16:30:45) ===
```
These headers contain all the data needed to build a history view. Currently, this data is only visible by manually reading the log file or catching it during the active operation in the RichLog widget.

The `orchestration-history` spec already exists in `openspec/specs/orchestration-history/spec.md` defining the requirements. The `tui-layout` spec needs a delta to add the widget to the actions column.

## Goals / Non-Goals

**Goals:**
- Parse orchestration log headers to extract action, services, and timestamp
- Display the 5 most recent operations below the action buttons in the actions column
- Use relative timestamps ("2h ago", "1d ago") for compactness
- Refresh history on startup and after each orchestration action

**Non-Goals:**
- Clickable history entries to replay or view full output
- Filtering or searching history
- Tracking operation duration or success/failure status
- Persisting history separately from the existing orchestration.log

## Decisions

### Log parsing via regex on header lines

Parse the existing `=== Action [services] (timestamp) ===` header format using a regex pattern. This avoids adding any new log format or data store — the orchestration.log is already the source of truth.

**Alternative considered**: A structured JSON history file written alongside the log. Rejected because it adds write complexity and a second source of truth for the same data.

### Textual Static widget for the history display

Use a `Static` widget that renders pre-formatted `Text` content, similar to `LinksPanel`. This is the simplest approach — no scrolling or interaction needed for 5 entries.

**Alternative considered**: A `ListView` or `DataTable` for history entries. Rejected because 5 static entries don't need scrolling or selection, and a `Static` widget keeps complexity minimal.

### Read only the last N lines of the log file

Instead of parsing the entire orchestration.log (which grows unbounded), read only the tail of the file to find recent headers. Read the last ~200 lines — more than enough to find 5 operation headers even with verbose command output between them.

**Alternative considered**: Parse the entire file. Rejected because the file grows over time and would get slower to parse.

### Relative timestamps with humanized format

Display timestamps as relative time ("5m ago", "2h ago", "3d ago") using stdlib `datetime`. This gives at-a-glance recency without consuming horizontal space.

## Risks / Trade-offs

- **[Log format coupling]** → The regex is tightly coupled to the `=== Action [services] (timestamp) ===` header format. Mitigation: this format is well-established and any changes would be made alongside the parser.
- **[File I/O on refresh]** → Reading the log tail on every 10-second refresh cycle adds minimal I/O. Mitigation: only read the last ~200 lines, and the file is local.
