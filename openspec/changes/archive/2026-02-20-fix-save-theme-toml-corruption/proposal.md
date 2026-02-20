## Why

`save_theme()` uses regex to modify the TOML config file, which corrupts it by writing escaped quotes (`name = \"nord\"` instead of `name = "nord"`). This causes a `TOMLDecodeError` crash on next startup. As more config values need write-back over time, regex-based TOML editing is fragile and error-prone.

## What Changes

- Replace regex-based TOML editing in `save_theme()` with `tomlkit` (a format-preserving TOML library)
- Add `tomlkit` as a runtime dependency
- Remove the `re` import if no longer needed elsewhere

## Capabilities

### New Capabilities

_(none)_

### Modified Capabilities

- `configuration`: Theme write-back implementation changes from regex to `tomlkit`, fixing the escaped-quotes bug. The spec-level behavior (save theme to file, preserve other content) is unchanged — this is a bug fix to meet existing requirements.

## Impact

- **Code**: `stacktui/dashboard.py` — `DashboardConfig.save_theme()` method
- **Dependencies**: New runtime dependency `tomlkit>=0.13` added to `pyproject.toml`
- **Config files**: No format changes — existing `dashboard.toml` files work as-is (once the corrupted ones are manually fixed)
