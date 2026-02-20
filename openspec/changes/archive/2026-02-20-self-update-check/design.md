## Context

StackTUI is run from a git clone. The existing `_self_update()` function pulls `PROJECT_ROOT` (the managed project's CWD) at startup, but the StackTUI package itself lives in a separate repo. There's no mechanism for users to know when StackTUI has upstream updates available while the dashboard is running.

The `WebhookBanner` widget already provides a pattern for showing transient notifications. The `_is_installed_package()` helper already distinguishes git-clone vs site-packages installs.

## Goals / Non-Goals

**Goals:**
- Detect when the StackTUI repo has upstream commits not yet pulled
- Show a visible, non-intrusive banner in the dashboard UI
- Check periodically without blocking the UI or overwhelming the network
- Extend the startup `_self_update()` to also pull the StackTUI repo

**Non-Goals:**
- Auto-updating StackTUI without user action (the banner informs, the user decides)
- Supporting update checks for pip/uv-installed packages (only git clones)
- Adding a button to trigger the update from within the TUI (restart handles it)

## Decisions

### Locating the StackTUI repo root
Walk up from `Path(__file__).resolve()` looking for a `.git` directory. This works for git clones and avoids hardcoding paths. Returns `None` for site-packages installs (checked via `_is_installed_package()`).

**Alternative considered**: Using `PROJECT_ROOT` — rejected because that's the managed project, not StackTUI itself.

### Update detection via git fetch + rev comparison
Run `git fetch` in the StackTUI repo, then compare `git rev-parse HEAD` vs `git rev-parse @{u}` and use `git rev-list HEAD..@{u} --count` to get the number of commits behind.

**Alternative considered**: `git remote show origin` — rejected because it's slower and output parsing is fragile.

### Check interval: 5 minutes
Service status polls every 10 seconds. Update checks involve a network fetch and only need to run infrequently. 5 minutes balances responsiveness with network/CPU cost.

### Banner placement
Place the `UpdateBanner` below the `WebhookBanner` in `col-git`. Both are hidden by default and only shown when relevant, so they don't compete for space.

### Thread worker for the check
The git fetch is a blocking network call. Run it in a `@work(thread=True)` method to avoid blocking the Textual event loop. Use `call_from_thread` to update the banner widget.

## Risks / Trade-offs

- **[Network failures]** → Git fetch may fail silently on network issues. Mitigation: wrap in try/except with short timeout (15s), fail silently — the banner just won't appear.
- **[No tracking branch]** → If the local branch has no upstream set, `@{u}` fails. Mitigation: catch the error and skip the check.
- **[Repo not found]** → StackTUI may be installed in ways that don't have a `.git` parent. Mitigation: `_get_stacktui_repo_root()` returns None, check is skipped entirely.
