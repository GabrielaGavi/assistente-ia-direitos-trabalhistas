# Color

KERNEL is a dark system with one flashlight. Four near-black grounds step up in tiny increments, three grays carry the text, and Flash Lime marks the single action that matters on a screen.

## Grounds

| Token | Name | Hex | Use |
| --- | --- | --- | --- |
| `--color-bg` | Void | #08090A | Page ground, deck slides |
| `--color-surface` | Carbon | #0F1011 | Cards, panels, table wrap, dialog |
| `--color-surface-2` | Console | #16171A | Inputs, raised cards, hover rows, secondary buttons |
| `--color-surface-3` | Graphite | #1C1D20 | Badges, key caps, selected sidebar item |

## Ink and edges

| Token | Name | Hex | Use |
| --- | --- | --- | --- |
| `--color-text` | Paper | #F7F8F8 | Headings, primary text |
| `--color-text-2` | Mist | #D0D6E0 | Body on cards, links, labels |
| `--color-muted` | Fog | #8A8F98 | Captions, metadata, issue IDs, nav links at rest |
| `--color-subtle` | Ash | #62666D | Disabled text and section labels in the app sidebar only |
| `--color-divider` | Hairline | #23252A | 1px card edges, table rows, section rules |
| `--color-border` | Wire | #383B3F | Control outlines, key caps, raised edges |

## Accents and status

| Token | Name | Hex | Use |
| --- | --- | --- | --- |
| `--color-accent` | Flash Lime | #E4F222 | One primary button per view, focus ring, checkbox fill |
| `--color-on-accent` | Void | #08090A | Text on Flash Lime |
| `--color-secondary` | Branch Violet | #6366F1 | In-progress dots, switches that are on, charts, text selection |
| `--color-success` | Success | #27A644 | Merged, deployed, passing |
| `--color-warning` | Warning | #F2994A | In review, slow, degraded |
| `--color-error` | Error | #EB5757 | Failed, blocked, invalid |
| `--color-info` | Info | #4EA7FC | Neutral notices |

## Rules

- Flash Lime is a flashlight: one filled button per view, plus the focus ring. Never use it for links, nav items, headings, borders, icons or large fills.
- No gradients and no glow. Depth comes from the ground steps and 1px hairlines.
- Status colors appear as a 6 to 8px dot next to a word, never as a filled badge or a tinted alert background.
- Branch Violet is a state color, not a second brand accent: keep it off buttons.

## Contrast (WCAG 2.x)

| Text on ground | Ratio |
| --- | --- |
| Paper on Void | 18.7:1 |
| Mist on Void | 13.6:1 |
| Fog on Void | 6.1:1 |
| Fog on Console | 5.5:1 |
| Void on Flash Lime | 16.2:1 |
| Error on Carbon | 5.5:1 |
| Success on Carbon | 6.0:1 |
| Ash on Void | 3.5:1 (large or disabled text only) |
