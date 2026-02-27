## 1. Helper Function

- [x] 1.1 Add `get_git_status_summary()` function near `get_git_info()` in `dashboard.py` that runs `git status --porcelain` via `_run()`, parses two-character status codes, and returns a compact summary string (e.g., `"3M 1S 2?"`, `"clean"`, or `""` on failure)

## 2. Subtitle Integration

- [x] 2.1 Update `on_mount` to include git status summary in the initial subtitle: `"{mode} | {branch}@{sha} | {summary}"`
- [x] 2.2 Update `_refresh_status()` to call `get_git_status_summary()` and update `self.sub_title` with the current summary
- [x] 2.3 Update `_do_git_pull` finally block to include git status summary when rebuilding the subtitle
- [x] 2.4 Update `_do_checkout` success path to include git status summary when rebuilding the subtitle

## 3. Verification

- [x] 3.1 Run the app with demo environment and verify dirty/clean states display correctly in the header subtitle
