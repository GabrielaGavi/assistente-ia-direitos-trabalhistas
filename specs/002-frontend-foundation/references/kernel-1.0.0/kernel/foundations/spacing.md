# Spacing, radius and elevation

## Spacing (4px base, compact)

| Token | Value | Typical use |
| --- | --- | --- |
| `--space-1` | 4px | Icon gaps, badge padding |
| `--space-2` | 8px | Inside controls, stacked labels |
| `--space-3` | 12px | Row gaps, alert padding |
| `--space-4` | 16px | Grid gap, control padding |
| `--space-5` | 24px | Card padding |
| `--space-6` | 32px | Page padding, doc stages |
| `--space-7` | 48px | Heading to content |
| `--space-8` | 64px | Mobile section gap |
| `--space-9` | 96px | Section gap (`--section-gap`) |

Density is compact inside components (controls are 28, 36 or 44px tall) and generous between sections. Content width is 1120px; text measure is 640px.

## Radius

| Token | Value | Use |
| --- | --- | --- |
| `--radius-badge` | 4px | Status badges, key caps, inline code |
| `--radius-control` | 10px | Buttons, inputs, selects, alerts, toasts, tabs |
| `--radius-surface` (`--radius`) | 12px | Cards, photos, tables, dialogs, product windows, capsules |
| `--radius-pill` | 999px | Filter tags, switches, progress bars |

Primary buttons are never pills: the 10px rectangle is part of the system's precision.

## Elevation

| Token | Value | Use |
| --- | --- | --- |
| `--shadow-1` | 1px Hairline ring | Every card and photo on the page |
| `--shadow-2` | Hairline ring + 8px/24px shadow | Toasts, capsules |
| `--shadow-3` | Wire ring + 24px/64px shadow | Dialogs, product windows |

## Grid

- `.kn-grid` auto-fits columns of at least 240px with a 16px gap; `.kn-grid--2` and `.kn-grid--3` fix the count and fall back to one column under 860px.
- Hairline rules (`.kn-section--rule`) separate landing sections instead of background changes.
