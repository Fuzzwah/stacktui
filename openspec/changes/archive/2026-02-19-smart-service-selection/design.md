## Context

The dashboard currently treats all action buttons identically regardless of service state, and selection controls are in a separate column from the service list. After `_do_git_pull()` detects affected services, it only logs them — it doesn't persist that information or auto-select those services. The `ServicePanel` tracks unhealthy services internally for auto-check logic but doesn't expose that state for other components to query.

All changes are in `dashboard.py` (single-file app, ~1545 lines).

## Goals / Non-Goals

**Goals:**
- Persist git-pull affected services as Dashboard instance state
- Auto-select affected services after git pull
- Show contextual action buttons based on the aggregate state of selected services
- Move selection controls (Select All, Changed, Unhealthy) to a horizontal row below the service list
- Expose ServicePanel health state for external querying

**Non-Goals:**
- Changing orchestration logic (stop/start/restart behavior stays the same)
- Adding new orchestration actions
- Persisting affected services across dashboard restarts

## Decisions

### 1. Store affected services on Dashboard instance

Add `self._affected_services: set[str] = set()` to `Dashboard.__init__()`. Updated in `_do_git_pull()` after `detect_affected_services()` returns. Cleared when irrelevant (e.g., after a restart of those services).

**Rationale**: Simple instance variable, no persistence needed. Cleared on restart which is the right behavior — after restarting affected services, the "changed" state is stale.

### 2. Expose ServicePanel health state via methods

Add `self._service_statuses: dict[str, str] = {}` to `ServicePanel` that maps service name to status_text. Populate it in `update_services()`. Add `get_unhealthy_services() -> set[str]` that returns services where status is not "healthy" and not "running". The existing `_prev_unhealthy` / `current_unhealthy` logic stays unchanged.

**Rationale**: The ServicePanel already computes this info in `update_services()` — just needs to store it for external access rather than using only local variables.

### 3. Selection controls in services column

Move "Select All" checkbox and add "Changed" / "Unhealthy" buttons into a `Horizontal(id="selection-controls")` container placed after the `ServicePanel` in `col-services`. The "Changed" and "Unhealthy" use `Button` widgets (not checkboxes) since they're one-shot select actions, not toggle states.

**Rationale**: Buttons are more intuitive for "select these now" actions vs. the toggle nature of "Select All". Placing them near the service list makes spatial sense — the actions column should only have action buttons.

### 4. Contextual button visibility logic

Replace `_update_action_visibility()` with logic that queries service states:
- Collect checked services and their status_text from ServicePanel
- If none checked: hide all buttons
- If all checked are healthy/running: show Restart + Stop only
- If all checked are stopped/exited/dim: show Start only
- Otherwise (mixed): show all three

Each button gets individual show/hide rather than toggling the container.

**Rationale**: Individual button visibility is cleaner than trying to manage container-level visibility with partial contents.

### 5. Clear affected services after restart

After a successful restart action completes in `_do_service_action()`, clear any services from `self._affected_services` that were just restarted.

**Rationale**: Once services are restarted with new code, they're no longer "changed" — the affected state is consumed.

## Risks / Trade-offs

- **[Race condition in git pull]** → `_do_git_pull` runs in a worker thread and sets `_affected_services`. Selection checkbox updates must use `call_from_thread`. Already the pattern used for auto-checking unhealthy services.
- **[Button flash on refresh]** → `_update_action_visibility()` is called on every checkbox change and every refresh. Could cause brief visual flicker if status changes between refreshes. → Mitigation: only update button visibility when the computed state actually changes.
- **[Select All semantics]** → "Select All" checkbox toggle-off should uncheck all. The Changed/Unhealthy buttons should only add to selection, not toggle. This avoids confusing interaction between the controls.
