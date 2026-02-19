## Context

StackTUI uses Textual's CSS design tokens (`$accent`, `$text`, `$warning-darken-2`) throughout its embedded CSS. Textual >=1.0 ships with a built-in theme system that maps these tokens to color palettes. The app currently uses the default `textual-dark` theme with no way to change it.

Textual provides ~8 built-in themes, a `Theme` class for custom themes, and automatic command palette integration (`Ctrl+P`) that lists all registered themes.

## Goals / Non-Goals

**Goals:**
- Let users cycle through themes with a keybinding
- Let users set a default theme in config
- Leverage Textual's built-in theme system (no custom theme infrastructure)

**Non-Goals:**
- Custom theme creation (users can do this later by registering `Theme` objects)
- Persisting theme selection across sessions (beyond the config default)
- Theme-specific CSS overrides

## Decisions

### 1. Use Textual's built-in `app.theme` and `app.available_themes`

**Rationale:** The app's CSS already uses design tokens, so switching `self.theme` immediately recolors everything. No CSS changes needed.

**Alternative considered:** Custom color variables in config — rejected as unnecessary complexity when Textual handles this natively.

### 2. Cycle themes with `Shift+T` keybinding

**Rationale:** Lowercase `t` is already bound to "Start". `Shift+T` is mnemonic and available. The action cycles through sorted theme names in `self.available_themes`.

### 3. Optional `[theme]` config section with `name` key

**Rationale:** Simple, single-key config. Applied in `on_mount()`. Invalid names fall back to Textual's default silently (Textual handles this gracefully).

### 4. Show current theme name in notification

**Rationale:** `self.notify(theme_name)` gives instant visual feedback when cycling. No persistent UI element needed.

## Risks / Trade-offs

- **[Risk]** Some custom CSS colors (e.g. hardcoded hex in widget styles) won't respond to theme changes → **Mitigation:** The current CSS uses design tokens, so this isn't an issue today. Document that future CSS should continue using tokens.
- **[Risk]** Theme name in config is misspelled → **Mitigation:** Textual ignores invalid theme names and keeps the default. No crash risk.
