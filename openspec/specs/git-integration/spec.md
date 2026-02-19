# Git Integration Specification

## Purpose

Git operations including pull, checkout, ref browsing, and affected service detection. All git operations run as threaded workers with output streamed to the orchestration log.

## Requirements

### Requirement: Git Pull

The system MUST support pulling latest code without restarting services.

#### Scenario: Successful git pull

- GIVEN the user presses Git Pull (or key `g`)
- WHEN `git pull` succeeds
- THEN the output streams to the orchestration log
- AND the dashboard subtitle updates with the new branch@sha
- AND the ref selector refreshes

#### Scenario: Git pull with changed files

- GIVEN `git pull` pulls new commits
- WHEN the old and new HEAD differ
- THEN `git diff --name-only old..new` identifies changed files
- AND `detect_affected_services()` maps them to services via path_map
- AND affected services are listed in the orchestration log

#### Scenario: Dashboard script self-update detection

- GIVEN `git pull` updates the `dashboard.py` file itself
- WHEN the changed files include the script's relative path
- THEN a "Reload Dashboard" button becomes visible

#### Scenario: Webhook signal cleanup

- GIVEN a webhook signal file exists and `git pull` succeeds with new commits
- WHEN the pull completes
- THEN the webhook signal file is deleted

### Requirement: Git Checkout

The system MUST support switching branches/refs from a dropdown.

#### Scenario: Branch checkout

- GIVEN the user selects a different branch in the ref dropdown
- WHEN the selected ref differs from the current ref
- THEN `git checkout <ref>` is executed
- AND the subtitle updates with the new branch@sha

### Requirement: Ref Selector

The system MUST display available git refs in a dropdown.

#### Scenario: Ref list population

- GIVEN the dashboard is mounted
- WHEN refs are fetched
- THEN `git fetch --prune` runs first
- AND `git branch -r` provides remote branches (stripping "origin/" prefix)
- AND `git log --oneline -10` provides recent commits
- AND the current branch is marked with an asterisk prefix

### Requirement: Self-Update on Startup

The system MUST auto-update from git on startup unless disabled.

#### Scenario: Startup self-update

- GIVEN `--no-update` flag is NOT set
- WHEN the application starts (before TUI loads)
- THEN `git pull --ff-only` runs
- AND if the script file's mtime changed, the process re-execs itself

#### Scenario: Skip self-update

- GIVEN `--no-update` flag IS set
- WHEN the application starts
- THEN no git pull is performed
