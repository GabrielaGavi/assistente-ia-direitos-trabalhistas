# AGENTS.md — KERNEL design system

Instructions for AI coding agents (Codex, Claude Code and others) working in this folder. The person you are working with always has the final say: when their request and these notes disagree, follow them.

## Project

KERNEL is a design system for developer tool and engineering SaaS sites: tokens, foundations, seven component families, a landing template and a 16:9 deck, in static HTML and CSS with no build step.

- Stack: static HTML and CSS. One stylesheet, `styles.css`, used by every page. The only script is the inline `showModal()` call in `components/dialog.html`.
- `README.md` is the buyer guide. `CREDITS.md` lists the images and the fonts the kit expects.

## Run it

- `python3 -m http.server 8080` or `npx serve .` in this folder, then open `http://localhost:8080`.

## Where things are

- Tokens: `theme.json` (source of truth for values) and the `:root` block in `styles.css` (the same values as CSS variables). Keep the two in sync.
- Component classes: `styles.css`, grouped by section comments (Layout, Type, Buttons, Cards and media, Forms, Navigation, Feedback, Table, Dialog). The `doc-*` classes at the end only style the kit's own documentation pages.
- Specimens: `components/*.html`. Templates: `templates/landing/index.html`, `templates/deck/index.html`.
- Rules in words: `foundations/*.md`.
- Photos: `assets/imagery/`, three 1920 x 1080 WebP files named by role.

## Rules for this project

- Change tokens, not components. New colors, sizes or radii go into `:root` and `theme.json` first, then get used through `var(--…)`.
- Flash Lime (`--color-accent`) fills one primary action per view. Never use it for links, navigation, headings, borders or large backgrounds.
- Never use a font weight above 500, a gradient, or a glow. Separate surfaces with the Void, Carbon, Console, Graphite steps and 1px hairlines (`--color-divider`, `--color-border`). Deep shadows are only for floating layers (dialog, toast, capsule, product window).
- Controls use `--radius-control` (10px), cards, photos and windows use `--radius-surface` (12px), status badges use `--radius-badge` (4px), filter tags and switches are pills.
- Issue IDs, versions, dates in logs and key hints use `--font-mono`. Everything else uses Mona Sans.
- Status is a small colored dot plus a word. Do not fill badges or alerts with status colors.
- Keep the product names, prices and metrics clearly fictional unless the user gives real ones.
- Keep pages accessible: real labels on inputs, `aria-current` on the current navigation item, alt text on every photo, visible focus rings.
- Keep the current look unless the user asks to change it. Before a large change, say what you plan to do.
- Fonts are not covered by the HorizonX license. If the user changes the fonts, use ones they own or have a license for, and never download font files they did not provide.
- When you add an image, font or library, add it to `CREDITS.md`.
- Do not add analytics, tracking or other third-party scripts unless the user asks for them.

## Check your work

1. Serve the folder and open `index.html`, `theme.html`, every page in `components/` and both templates.
2. Make sure the browser console shows no errors and no file returns 404.
3. Check the layout at 390 px and 1440 px wide.
4. If you changed colors, check text contrast is at least 4.5:1 for body text (the current values are listed in `foundations/color.md`).

## License

The design system is licensed to its owner through their HorizonX membership. Building and shipping sites from it is allowed; publishing or reselling the source files as a design system or template is not. Terms: https://horizonx.so/terms
