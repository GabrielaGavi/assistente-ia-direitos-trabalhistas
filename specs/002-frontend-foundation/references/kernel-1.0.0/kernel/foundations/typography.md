# Typography

One grotesque family, Mona Sans, from Light 300 to Medium 500, plus Fragment Mono for issue IDs, versions, log dates and key hints. Mona Sans stands in for the proprietary neo-grotesk this style is usually set in; Fragment Mono stands in for its monospace companion.

- `--font-heading` and `--font-body`: Mona Sans. `--font-mono`: Fragment Mono.
- Heading weight 500, body weight 400. **Medium 500 is the heaviest weight.** Never use 600 or bold.
- Big type tracks tight (negative letter-spacing); body text stays at 0.

## Scale

| Token | Size / line | Weight | Tracking | Use |
| --- | --- | --- | --- | --- |
| Display | 64px / 1.0 | 500 | -0.022em | Landing hero |
| H1 | 48px / 1.05 | 500 | -0.02em | Page and section titles |
| H2 | 32px / 1.12 | 500 | -0.015em | Section titles, photo overlays |
| H3 | 24px / 1.2 | 500 | -0.01em | Sub-sections |
| H4 | 20px / 1.3 | 500 | -0.005em | Card and dialog titles |
| H5 | 15px / 1.4 | 500 | 0 | Group headers, table captions |
| H6 (mono) | 12px / 1.4 | 400 | 0.02em | Eyebrows and issue IDs, e.g. `KRN-1024` |
| P1 | 17px / 1.6 | 400 | 0 | Ledes |
| P2 | 15px / 1.55 | 400 | 0 | Body (default) |
| P3 | 13px / 1.5 | 400 | 0 | Card text, captions, table metadata |

On screens under 860px the display drops to 44px, H1 to 36px and H2 to 26px.

## Rules

- Eyebrows are monospace issue IDs or short tags in Fog, never uppercase sans labels.
- Keep line length at or under 64 characters (`--text-width: 640px`).
- Numbers in tables use tabular figures (`.kn-num`).
- Do not set body copy in Paper on Carbon cards; use Mist or Fog so headings stay the brightest thing on the card.
