# KERNEL design system

A design system for developer tool and engineering SaaS sites (issue tracking, CI/CD, observability, API platforms): a midnight precision instrument with near-black surfaces, paper-white type at tight tracking, hairline edges and one acid-lime accent used like a flashlight. Tokens, foundations, seven component families, a product landing page and a 16:9 launch deck, all in plain HTML and CSS.

Made by HorizonX · Version 1.0.0 · October 2026

## Start here

1. Unzip this folder.
2. Start a local web server inside it:
   - With Python (already installed on Mac and Linux): `python3 -m http.server 8080`
   - Or with Node.js: `npx serve .`
3. Open `http://localhost:8080` in your browser (with `npx serve`, use the address it prints).

There is no build step and nothing to install. `index.html` links to every page in the kit.

## What's inside

- `theme.json`: every token (color, type scale, spacing, radius, elevation, imagery roles) in one machine-readable file.
- `styles.css`: the same tokens as CSS custom properties, plus the component classes (all start with `kn-`). Every page in the kit uses only this stylesheet.
- `index.html`: overview of the kit. `theme.html`: the tokens rendered as swatches, a type scale, spacing bars and radius samples.
- `foundations/`: `color.md`, `typography.md`, `spacing.md` (spacing, radius, elevation, grid), `imagery.md` (the three photo roles and how to crop them) and `patterns.md` (product window, issue IDs, status capsule, page rhythm).
- `components/`: `buttons.html`, `cards.html`, `dialog.html`, `forms.html`, `navigation.html`, `feedback.html`, `table.html`, and `index.html` listing them.
- `templates/landing/index.html`: a full product site for a fictional issue tracker and deploy log (banner, sticky bar, hero with an HTML product window, metrics, features, observability photo band, deploys, changelog, pricing, call to action, footer).
- `templates/deck/index.html`: a six-slide 16:9 launch deck. Print it to PDF (landscape, no margins) to export.
- `assets/imagery/`: three 1920 x 1080 WebP photos, one per imagery role (space, material, object).
- `README.md` (this guide), `CREDITS.md` (images and fonts), and `AGENTS.md` plus `CLAUDE.md` (instructions for AI coding agents).

## Make it yours

- **Brand colors:** change the `--color-*` values at the top of `styles.css` and the matching entries in `theme.json`. Keep one accent for the primary action and let the grounds do the rest.
- **Type:** change `--font-heading`, `--font-body` and `--font-mono`. Keep weights at 500 or lighter and keep big type tracked tight.
- **Shape:** `--radius-control` (buttons, inputs), `--radius-surface` (cards, windows, photos), `--radius-badge` and `--radius-pill` control every corner.
- **Copy and product:** the landing page and deck use a fictional product, Ferrule, with placeholder prices and metrics. Replace the text directly in the HTML.
- **Photos:** replace the files in `assets/imagery/` and keep the same names, or update the `src` paths. Follow the roles in `foundations/imagery.md`.

## Using it in a framework

The classes are framework-agnostic. To use KERNEL in React, Svelte, Vue or Tailwind, import `styles.css` once (or map the `:root` variables into your Tailwind theme) and copy the markup from the component pages.

## Keep building with AI

Open this folder in an AI coding agent such as Claude Code or Codex and ask in plain words. The folder includes `AGENTS.md` (and a `CLAUDE.md` that points to it), so coding agents learn how the system is built and how to check their work before they change anything. Some examples:

- "Read README.md and styles.css, then change the accent to my brand color: …"
- "Build a pricing page for my API product with the KERNEL components and the landing template as a starting point."
- "Port KERNEL to a Tailwind CSS theme and a set of React components without changing how it looks."

To add more HorizonX components from your agent, connect the HorizonX MCP server (included in your membership): https://horizonx.so/mcp

## Fonts

The kit is set in Mona Sans with Fragment Mono for issue IDs and code, loaded from Google Fonts by the `@import` at the top of `styles.css`. Both are open-source families chosen as close stand-ins for the neo-grotesk and monospace pairing this style is known for. Fonts are not covered by the HorizonX license: install or replace them with fonts you own or have a license for. Without them the pages fall back to your system sans-serif and monospace.

## License

Your HorizonX membership gives you a commercial license for this design system: use it and adapt it in personal, client and commercial projects. You may not resell, redistribute, sublicense or publicly share the original source files. Full terms: https://horizonx.so/terms.
Images are listed in `CREDITS.md`.

## Need help?

Write to support@horizonx.so and mention **KERNEL**.
