## Context

The center column of the dashboard (`col-services`) currently contains:
1. `ServicePanel` — service checkboxes + status dots, with a `#data-freshness` Static at the bottom
2. A `Horizontal(id="selection-controls")` row with: "All" Checkbox, "Changed" Button (hidden by default), "Unhealthy" Button (hidden by default)

The buttons have `height: 1` CSS which clips their labels, making them appear as blank colored rectangles. The freshness display is positioned below the services and is easy to miss.

## Goals / Non-Goals

**Goals:**
- Move freshness display above the service list for better visibility
- Replace the broken selection controls (checkbox + buttons) with a single Select dropdown
- Provide five selection modes: All, Changed, Stopped, Running, None
- Keep the dropdown always visible (no conditional show/hide)

**Non-Goals:**
- Changing the service checkbox behavior itself
- Modifying how services are orchestrated after selection
- Adding multi-select to the dropdown (it's a mode selector, not a multi-picker)

## Decisions

### Use Textual Select widget instead of buttons

**Decision**: Replace the Checkbox + Button row with a `Select` dropdown.

**Rationale**: A Select widget is a standard Textual pattern already used elsewhere in the app (ref selector, log service selector). It handles its own rendering correctly at any height, avoids the CSS clipping issue, and consolidates 3 controls into 1. The dropdown also scales better — adding new selection modes (Stopped, Running) is just adding tuples.

**Alternative considered**: Fix the button heights. This would solve the rendering bug but still leave a cluttered row of controls that grows with each new selection mode.

### Selection is "fire and forget" — dropdown resets after applying

**Decision**: When the user picks an option, the checkboxes update and the Select resets to blank (prompt text). The dropdown acts as a command, not persistent state.

**Rationale**: The user may pick "All" then manually uncheck one service. If the dropdown showed "All" it would be misleading. Resetting to blank after each selection avoids stale state.

### Move freshness inside ServicePanel, above service rows

**Decision**: Reposition the `#data-freshness` Static from after the service rows to before them, right after the "Services" title.

**Rationale**: Freshness is a key status indicator. Placing it at the top of the panel makes it visible without scrolling.

## Risks / Trade-offs

- [Minor UX shift] Users accustomed to the "All" checkbox lose a toggle — the dropdown has "All" and "None" as separate options instead. → Acceptable since the checkbox was the only working control; the dropdown is strictly more capable.
- ["Changed" always visible] Previously the Changed button was hidden when no affected services existed. Now "Changed" is always in the dropdown but does nothing if `_affected_services` is empty. → Low risk; selecting it with no affected services simply unchecks everything, which is the same as "None".
