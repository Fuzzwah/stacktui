## Why

The UpdateBanner currently shows a passive text message ("restart to update") when StackTUI is behind upstream, but provides no way to act on it. The user must manually restart the process. Adding a CTA button directly in the banner lets the user pull updates and restart with a single click.

## What Changes

- Convert `UpdateBanner` from a text-only `Static` widget to a container with both a text label and a "Restart to Update" button
- The button pulls the StackTUI repo (`git pull --ff-only`) then re-execs the process (same `os.execv` pattern used by the existing Reload Dashboard button)
- Remove the " — restart to update" text suffix since the button replaces it

## Capabilities

### New Capabilities

_(none — this enhances an existing capability)_

### Modified Capabilities

- `self-update-check`: The update banner now includes an interactive restart button instead of passive text

## Impact

- **Code**: `UpdateBanner` class in `stacktui/dashboard.py` changes base class from `Static` to `Horizontal` and gains a `compose()` method; new button press handler added to `Dashboard`
- **Dependencies**: None (uses existing Textual `Button` widget already imported)
- **UX**: Banner becomes interactive; no breaking changes to keyboard shortcuts or other workflows
