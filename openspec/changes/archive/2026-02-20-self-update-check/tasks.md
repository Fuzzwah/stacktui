## 1. Helper Functions

- [x] 1.1 Add `_get_stacktui_repo_root()` — walk up from `Path(__file__).resolve()` to find `.git`, return `Path | None`. Skip if `_is_installed_package()`.
- [x] 1.2 Add `_check_stacktui_updates()` — run `git fetch` and `git rev-list HEAD..@{u} --count` in the StackTUI repo. Return int (commits behind) or 0 on any failure. Use 15s timeout.

## 2. UpdateBanner Widget

- [x] 2.1 Create `UpdateBanner` class modeled on `WebhookBanner` — hidden by default, styled with an info/accent color
- [x] 2.2 Add `show_update(count: int)` method to display "StackTUI update available (N commits behind) — restart to update"
- [x] 2.3 Add `hide()` method to remove the visible class

## 3. Dashboard Integration

- [x] 3.1 Add `UpdateBanner` to the `compose()` layout in `col-git`, above the `WebhookBanner`
- [x] 3.2 Add `_check_for_self_update()` threaded worker that calls `_check_stacktui_updates()` and updates the banner via `call_from_thread`
- [x] 3.3 Call `_check_for_self_update()` in `on_mount()` and set up a 5-minute `set_interval`

## 4. Startup Self-Update

- [x] 4.1 Extend `_self_update()` to also `git pull --ff-only` the StackTUI repo when it differs from `PROJECT_ROOT`
