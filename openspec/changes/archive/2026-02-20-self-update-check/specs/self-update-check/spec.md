## ADDED Requirements

### Requirement: StackTUI repo root detection
The system SHALL locate the StackTUI package's own git repository by walking up from the package file path. If running from site-packages or no `.git` directory is found, the check SHALL be skipped.

#### Scenario: Git clone install
- **WHEN** StackTUI is running from a git clone (not site-packages)
- **THEN** `_get_stacktui_repo_root()` returns the path to the nearest parent directory containing `.git`

#### Scenario: Package install
- **WHEN** StackTUI is installed via pip/uv into site-packages
- **THEN** `_get_stacktui_repo_root()` returns `None`

### Requirement: Upstream update detection
The system SHALL check whether the StackTUI repo's local branch is behind its upstream tracking branch by running `git fetch` followed by `git rev-list HEAD..@{u} --count`.

#### Scenario: Updates available
- **WHEN** the upstream tracking branch has 3 commits not present locally
- **THEN** `_check_stacktui_updates()` returns `3`

#### Scenario: Already up to date
- **WHEN** the local branch matches the upstream tracking branch
- **THEN** `_check_stacktui_updates()` returns `0`

#### Scenario: No tracking branch
- **WHEN** the local branch has no upstream tracking branch configured
- **THEN** `_check_stacktui_updates()` returns `0`

#### Scenario: Network failure
- **WHEN** `git fetch` fails due to network issues or times out (15s)
- **THEN** `_check_stacktui_updates()` returns `0` without raising an exception

### Requirement: Periodic background check
The system SHALL check for StackTUI updates on mount and every 5 minutes thereafter. The check MUST run in a background thread to avoid blocking the UI.

#### Scenario: Initial check on mount
- **WHEN** the dashboard mounts
- **THEN** the update check runs once immediately

#### Scenario: Periodic re-check
- **WHEN** 5 minutes have elapsed since the last check
- **THEN** the update check runs again

### Requirement: Update banner display
The system SHALL display an `UpdateBanner` widget when updates are available, showing the number of commits behind. The banner SHALL be hidden when the local copy is up to date.

#### Scenario: Updates available
- **WHEN** `_check_stacktui_updates()` returns a value greater than 0
- **THEN** the UpdateBanner is visible with text indicating the number of commits behind and a suggestion to restart

#### Scenario: No updates
- **WHEN** `_check_stacktui_updates()` returns `0`
- **THEN** the UpdateBanner is hidden

### Requirement: Startup self-update includes StackTUI repo
The `_self_update()` function SHALL also pull the StackTUI repo (if it differs from `PROJECT_ROOT`) before re-exec detection.

#### Scenario: StackTUI repo differs from PROJECT_ROOT
- **WHEN** `_self_update()` runs and the StackTUI repo root is different from `PROJECT_ROOT`
- **THEN** `git pull --ff-only` is run in the StackTUI repo root as well

#### Scenario: StackTUI repo is same as PROJECT_ROOT
- **WHEN** the StackTUI repo root equals `PROJECT_ROOT`
- **THEN** no additional pull is performed (existing pull covers it)
