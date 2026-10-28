# Patterns

## Product window

`.kn-window` is the HTML "screenshot": a Carbon frame with three Graphite dots, a 36px title bar and an optional 200px sidebar. Fill it with real components (issue rows, badges, avatars) instead of a raster image so it stays sharp and editable. Use it in the landing hero and on deck slides.

## Issue IDs as eyebrows

Above every title, put a short monospace tag in Fog: an issue ID (`KRN-1024`), a pipeline (`CI-42`), a date (`2026-10-14`) or a version (`v2.14.0`). This replaces uppercase sans labels everywhere.

## One flashlight per view

Each viewport gets exactly one Flash Lime button. In the landing page, the hero owns it; the nav "Sign up" and the closing call to action use the secondary style, and the Team pricing card gets the lime "Start building" because it is the only conversion action in that view.

## Status capsule

`.kn-capsule` floats over a photo or a window: a green dot, a short status ("Build passed in 42 s") and one small button. 12px corners, blurred Void fill, never a pill.

## Page rhythm

Banner, sticky bar, hero with product window, metrics row, three feature cards, photo band, split section, changelog, pricing, photo call to action, footer. Sections are 96px apart and separated by hairline rules, not by color bands.
