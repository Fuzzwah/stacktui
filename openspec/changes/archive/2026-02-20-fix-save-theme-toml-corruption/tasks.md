## 1. Dependencies

- [x] 1.1 Add `tomlkit>=0.13` to `pyproject.toml` dependencies
- [x] 1.2 Add `import tomlkit` to `dashboard.py`
- [x] 1.3 Run `uv sync` to install the new dependency

## 2. Fix save_theme()

- [x] 2.1 Replace regex-based `save_theme()` with `tomlkit.parse()` / `tomlkit.dumps()` implementation
- [x] 2.2 Remove `import re` if no longer used elsewhere in the file

## 3. Verify

- [ ] 3.1 Run StackTUI, cycle theme with `T`, confirm `dashboard.toml` has valid TOML (no backslash-escaped quotes)
- [ ] 3.2 Restart StackTUI and confirm it loads without `TOMLDecodeError`
- [ ] 3.3 Test theme save when `[theme]` section doesn't exist — confirm it's created correctly
