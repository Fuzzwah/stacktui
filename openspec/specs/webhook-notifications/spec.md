# Webhook Notifications Specification

## Purpose

Display banner notifications when a GitHub webhook reports new commits pushed to the current branch. Uses a JSON signal file written by an external webhook receiver.

## Requirements

### Requirement: Webhook Signal File Monitoring

The system MUST check for a GitHub push signal file on each status refresh.

#### Scenario: New commits available

- GIVEN a file at `{logs_dir}/github_push.json` exists
- AND its `branch` field matches the current git branch
- AND its `after` SHA does not match the local HEAD
- WHEN the status refresh runs
- THEN the WebhookBanner is shown with commit count, pusher, and latest message

#### Scenario: Signal for different branch

- GIVEN the signal file's `branch` field does not match the current branch
- WHEN the status refresh runs
- THEN the WebhookBanner remains hidden

#### Scenario: Already up to date

- GIVEN the signal file's `after` SHA matches the local HEAD (first 12 chars)
- WHEN the status refresh runs
- THEN the WebhookBanner remains hidden

#### Scenario: No signal file

- GIVEN no `github_push.json` file exists
- WHEN the status refresh runs
- THEN the WebhookBanner remains hidden

### Requirement: Banner Display

The WebhookBanner MUST show commit information clearly.

#### Scenario: Banner content

- GIVEN push data with 3 commits from "alice" with latest message "Fix login bug"
- WHEN the banner is shown
- THEN it displays "3 new commits from alice: Fix login bug"
- AND "3 new commits" is styled bold yellow
- AND the commit message is styled italic

### Requirement: Signal File Format

The signal file MUST be a JSON object with specific fields.

#### Scenario: Expected JSON structure

- GIVEN a webhook receiver writes to `github_push.json`
- WHEN the file is read
- THEN it contains: `branch` (string), `after` (SHA string), `pusher` (string), `commits` (array of objects with `message`, `id`, `timestamp`)
