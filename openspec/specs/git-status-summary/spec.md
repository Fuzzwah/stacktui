# Git Status Summary Specification

## Purpose

Display a summary of uncommitted changes (modified, staged, untracked file counts) in the git info area. Critical for knowing whether the working directory is clean before pulling or switching branches.

## Requirements

### Requirement: Git Status Query

The system MUST query git for working directory state using `git status --porcelain` via the existing `_run()` helper.

#### Scenario: Query working directory status

- **WHEN** the git status summary is collected
- **THEN** the system runs `git status --porcelain` via `_run()`
- **AND** parses the two-character status codes to count files by category

#### Scenario: Clean working directory

- **WHEN** `git status --porcelain` returns empty output
- **THEN** the function returns a string indicating clean state (e.g., `"clean"`)

#### Scenario: Git command failure

- **WHEN** `git status --porcelain` fails or times out
- **THEN** the function returns an empty string
- **AND** the subtitle omits the status segment rather than showing an error

### Requirement: Change Categorization

The system MUST categorize changes into staged, modified, and untracked groups.

#### Scenario: Staged files

- **WHEN** files have index changes (first character is `M`, `A`, `D`, `R`, or `C`)
- **THEN** the count of staged files is tracked and displayed with an `S` suffix

#### Scenario: Modified files

- **WHEN** files have working-tree changes (second character is `M` or `D`)
- **THEN** the count of modified files is tracked and displayed with an `M` suffix

#### Scenario: Untracked files

- **WHEN** files have status `??`
- **THEN** the count of untracked files is tracked and displayed with a `?` suffix

### Requirement: Status Display in Header Subtitle

The git status summary MUST appear in the header subtitle alongside existing branch and SHA information.

#### Scenario: Dirty state display

- **WHEN** uncommitted changes exist (e.g., 3 modified, 1 staged, 2 untracked)
- **THEN** the subtitle shows `"{mode} | {branch}@{sha} | 3M 1S 2?"`
- **AND** only non-zero categories are included in the summary

#### Scenario: Clean state display

- **WHEN** the working directory is clean
- **THEN** the subtitle shows `"{mode} | {branch}@{sha} | clean"`

#### Scenario: Error/empty state display

- **WHEN** the git status query fails or returns an empty result
- **THEN** the subtitle shows `"{mode} | {branch}@{sha}"` with no status segment

### Requirement: Status Refresh

The git status summary MUST stay current via the existing refresh mechanisms.

#### Scenario: Refresh on timer

- **WHEN** the `_refresh_status()` method runs on the 10-second interval
- **THEN** the git status summary is re-queried
- **AND** the header subtitle is updated with the current summary

#### Scenario: Refresh after git pull

- **WHEN** a git pull operation completes
- **THEN** the git status summary is refreshed immediately in the finally block
- **AND** the subtitle reflects the post-pull working directory state

#### Scenario: Refresh after git checkout

- **WHEN** a git checkout operation completes successfully
- **THEN** the git status summary is refreshed immediately
- **AND** the subtitle reflects the post-checkout working directory state
