# Adding a new page to the Paris 2026 guide

This repo is a set of self-contained static pages published via GitHub Pages at
**https://crumley.github.io/paris-2026/**. Each board (`paris.html`, `jul15-dinner.html`,
`crepes.html`, `chartres.html`) is one HTML file that is **data-driven**: a `PLACES`
array renders both the map pins and the cards. There is a Leaflet map and a
"show my location" blue dot on every page.

## Golden rule

**Clone the newest good page and edit its data. Do not hand-roll a page.**
The canonical reference implementation is **`crepes.html`** (newest, cleanest: has the
geolocation blue dot, the facts list, and the GF info box). Copy it, then change the
content. This guarantees the CSS, the SRI-pinned Leaflet, the pin rendering, and the
geolocation control all stay identical across pages.

## Anatomy of a page

- **`<head>`**: `<meta name="robots" content="noindex">`, mobile viewport, and the Leaflet
  **CSS with the exact SRI `integrity=` hash** - copy verbatim, do not change it.
- **`<style>`**: a `:root` block of color tokens (one per category) plus the shared card /
  map / pin / `.user-dot` / `.leaflet-locate` classes. Keep these; only edit the `:root`
  category colors for your page.
- **Body**: `header` (h1 + `.sub` + `.back` link to `./`) → optional `.caveat` box →
  `#map` → `.legend` → `#cards` grid → optional `.note` box → `footer`.
- **`<script>`**: Leaflet JS **with the exact SRI hash** (copy verbatim) → `COLORS` +
  `VLABEL` maps → the `PLACES` array → `mapUrl()` → map init (`fitBounds`, `scrollWheelZoom:false`)
  → the **geolocation IIFE** (the `◎` locate control + blue dot - copy verbatim) → the
  card-render loop.

## Data model (`PLACES`)

Each entry:

```js
{ name:"…", v:"<categoryKey>", emoji:"📍",
  tagline:"one line", blurb:"a paragraph",
  addr:"7 Rue de l'Échelle, 75001", dist:"…", hours:"…", price:"…", phone:"…",
  site:"https://…", lat:48.864, lon:2.334,
  anchor:true,                 // optional: the "you are here / main" pin, styled differently
  gfSafe:"…", gfAvoid:"…" }     // optional: renders the green/red info box
```

- **`v`** is the category key. Define every key you use in **both** `COLORS` (hex) and
  `VLABEL` (pill label). Pick a small, page-appropriate set (e.g. dinner board uses
  `top/gf/solid/splurge/consider`; crêpe page uses `matisse/galette/safe/alt`).
- Fields that are empty are omitted from the card automatically - only set what you have.
- Inline links inside `blurb`/`note` must use **single-quoted** attributes
  (`<a href='paris.html'>…</a>`) because the JS strings are double-quoted and rendered via
  `innerHTML`.

## Steps to add a page

1. **Gather the content** (places, addresses, hours, notes, one or two verdicts/categories).
2. **Geocode every address** to `lat`/`lon`:
   ```bash
   python3 tools/geocode.py "Grand Palais|Grand Palais, Paris, France" \
                            "Buckwheat|7 Rue de l'Echelle, 75001 Paris, France"
   ```
   (Uses Nominatim with the required User-Agent and a ~1.2s throttle. If a query returns
   NO RESULT, simplify it - drop the street number or use the landmark name.)
3. **Clone** `crepes.html` → `yourpage.html`. Edit: `<title>`, header h1/sub, the `.caveat`,
   the `:root` category colors, `COLORS`/`VLABEL`, the `PLACES` array, the legend, and the
   `.note`. Leave the CSS scaffold, SRI hashes, and geolocation IIFE untouched.
4. **Validate the inline JS before publishing** (prevents blank-page bugs):
   ```bash
   node tools/validate.js yourpage.html   # must print "OK: script parsed and ran…"
   ```
5. **Link it** from `index.html` - add an `<a href="yourpage.html">…</a>` to the
   `.toplinks` bar, and a day's todo/note if it's tied to a specific day.
6. **Publish from the repo root** (`/Users/ryan/paris-2026`, not a scratch dir):
   ```bash
   git add yourpage.html index.html && git commit -m "Add …" && git push origin main
   ```
7. **Confirm it went live**:
   ```bash
   gh api repos/crumley/paris-2026/pages/builds/latest --jq '.status + " " + .commit'
   # poll until "built <sha>", then:
   curl -s -H "Cache-Control: no-cache" https://crumley.github.io/paris-2026/yourpage.html | grep -o "<a PLACES name>"
   ```

## Conventions / guardrails

- **Never** put flight numbers, e-tickets, frequent-flyer numbers, seat assignments, or
  booking references on any page. The pages are `noindex` but still publicly reachable.
  Hotel names for planning are fine; booking/payment details are not.
- Mobile-first. Keep `scrollWheelZoom:false`, emoji teardrop pins, and the `◎`
  show-my-location button.
- Use ` - ` (spaced hyphen), not em-dashes, in copy to match the existing pages.
- Best quality comes from writing the `blurb`s from real research (hours, addresses,
  gluten notes, distances), not generic filler.
