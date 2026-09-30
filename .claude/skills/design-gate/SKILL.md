---
name: design-gate
description: "MANDATORY gate before writing any UI code. Blocks generic AI-looking websites and apps. Use whenever building, redesigning, or reviewing a website, landing page, web app, dashboard, portfolio, marketing site, artifact, or any .html/.tsx/.jsx/.vue/.svelte/.astro page or component. Forces a committed art direction, bans known AI-slop patterns (purple-blue gradients, Inter display type, centered hero + three icon cards, uniform rounded-2xl shadow-lg, gradient text headlines, emoji icons, generic copy), and provides a runnable audit that scores the output. Triggers on: design, redesign, build a site, make it look better, make it modern, premium, high-end, not generic, looks like AI made it, improve the UI, landing page, hero section, art direction, visual identity."
---

# Design Gate

Generic output is a process failure, not a taste failure. It happens when code gets written before a direction is chosen. This skill installs the missing step.

## The gate (do not skip)

Before writing a single line of UI code, output this brief. Six lines, no prose:

```
DIRECTION:  <one named direction from references/directions.md — e.g. "Swiss editorial + WebGL grain">
REFERENCE:  <2-3 real sites/studios this should feel like, and the ONE thing borrowed from each>
TYPE:       <display face> / <workhorse face> — scale ratio <n>, tracking rules
COLOR:      <dominant hue family> + <single accent> — OKLCH anchors, light & dark
DEPTH:      <how this page earns depth: 3D object / shader field / parallax layers / physical texture>
BREAK:      <the one deliberate rule-break per page: asymmetry, overlap, bleed, oversized type, off-grid>
```

If the user gave no direction, pick one and say which you picked and why in one sentence. Do not ask permission to have taste. Do not offer three options and stall.

Then build. Then run the audit.

## Hard bans

These ship in ~90% of AI-generated pages. They are the tell. Never produce them:

| Banned | Instead |
|---|---|
| `from-purple-* to-blue-*` / indigo→violet gradient | One hue family, derived in OKLCH; accent used under 10% of surface |
| Inter / Roboto / Open Sans as the **display** face | A display face with a real voice; Inter is fine as the workhorse only |
| Centered hero: h1 → subtitle → "Get Started" + "Learn More" | Asymmetric hero; one CTA with a specific verb; type set large enough to be a graphic element |
| Three feature cards, identical, icon in a rounded square | Vary card weight and size; at least one card breaks the row |
| `rounded-2xl shadow-lg` on every surface | Two surface treatments max; earn elevation, don't spray it |
| Gradient text on the headline (`bg-clip-text text-transparent`) | Solid ink. If the headline needs help, the typeface is wrong |
| Emoji as iconography (🚀 ✨ 💡 🔒) | One icon set, consistent stroke, or no icons |
| Every section `py-20 max-w-7xl mx-auto px-4` | Vary section rhythm; let one section bleed full-bleed edge to edge |
| Dark mode = `bg-gray-900` | Tinted near-black derived from the brand hue; raise surfaces with hue, not just lightness |
| Untouched shadcn/ui defaults | Override radius, border color, shadow, and font before using |
| Fake testimonials, ★★★★★ rows, stock avatars | Real quotes or no quotes. Omit the section |
| Copy: "Elevate", "Seamlessly", "Unlock the power of", "Transform your" | Say the specific thing the product does, in the user's words |
| `backdrop-blur` glass as the entire visual idea | Glass is an accent on one surface, not a style |
| Placeholder lorem, `via.placeholder.com`, gray boxes | Real content, or generated imagery (see `web-3d`, Pollinations, Canva MCP) |

## Non-negotiable floor

Every page ships with all of these, no exceptions:

1. **Type scale with contrast** — display step at least 4× body. Timid type reads as generic.
2. **One moment of depth** — see `web-3d`. A flat page needs one thing that isn't flat.
3. **Entrance choreography** — staggered reveal, not everything at once. See `motion-system`.
4. **`prefers-reduced-motion`** honored, and a static fallback that still looks designed.
5. **Contrast ≥ 4.5:1** on body text, visible focus rings, 44px touch targets.
6. **Real dark mode** if dark mode exists at all — tokens on `:root`, redefined, not inverted.
7. **Mobile at 375px** with no horizontal scroll and a 16px gutter.

## Audit before you call it done

```bash
python3 .claude/skills/design-gate/scripts/audit.py <file-or-dir>
```

Exits non-zero on any hard ban. Prints a 0-100 distinctiveness score with the specific line numbers. A page that scores under 70 is not finished. Fix the findings, don't argue with them.

## Then verify in a real browser

The audit reads source; it cannot see layout. Render the page before calling it done.
Chromium is pre-installed in Claude cloud containers (Playwright at
`/opt/node22/lib/node_modules/playwright`, browsers at `/opt/pw-browsers`) — launch with
`--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader` for WebGL.

Check at 375 / 768 / 1400px, in both colour schemes, and with reduced motion emulated:

```js
// Per-ELEMENT overflow. A document-level scrollWidth check is not enough:
// `overflow-x: clip` on <html> hides the symptom while content is still clipped.
await page.evaluate((vw) => [...document.querySelectorAll('body *')].filter(el => {
  const r = el.getBoundingClientRect();
  return (r.width && (r.right > vw + 1.5 || r.left < -1.5))
      || (el.scrollWidth > el.clientWidth + 2 && getComputedStyle(el).overflowX === 'visible');
}).map(el => el.tagName + '.' + el.className), 375);
```

Decorative, `aria-hidden` elements inside a clipping container are allowed to report
overflow. Anything carrying content is not.

## Worked example

`assets/reference-page.html` — a complete page in the "Warm Utilitarian" direction that
scores **100/100**: OKLCH token system, tabular data treated as the hero, a raw-WebGL
heat-haze field (tier 2, no library, no CDN), IntersectionObserver stagger, real dark
mode, and reduced-motion and no-WebGL fallbacks. Verified rendering at 375-1400px with
zero element overflow. Read it when a direction brief needs to become code.

## Depth references

- `references/directions.md` — 12 committed art directions with concrete tokens, type pairings, and what each is *for*. Read this when picking DIRECTION.
- `references/anti-slop.md` — why each ban exists, with the fix pattern in code.
- `references/tokens.md` — OKLCH token system, dark-mode derivation, type scale math.

## Related skills

- `web-3d` — Three.js / R3F / shader recipes for the DEPTH line.
- `motion-system` — GSAP / Motion choreography for the entrance requirement.
- `ui-ux-pro-max` — the style/palette/font *database*. Use it to look things up after the direction is chosen, never to pick the direction.
