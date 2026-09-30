---
name: motion-system
description: "Motion and micro-interaction design for web UI. Use when adding animation, transitions, scroll effects, page reveals, hover states, stagger, parallax, marquee, counters, page transitions, loading states, or when asked to make a site feel alive, smooth, polished, premium, or animated. Covers CSS-first motion, View Transitions, scroll-driven animations, GSAP ScrollTrigger, Motion (Framer Motion), easing and timing tokens, choreography, and prefers-reduced-motion. Satisfies the entrance-choreography requirement in design-gate."
---

# Motion System

Motion is hierarchy expressed in time. Everything appearing at once, with the same
duration and the same ease, is the animation equivalent of `shadow-lg` on every card.

> **Versions verified 2026-09-30** against the npm registry: `gsap@3.15.0`,
> `motion@13.4.6` (= `framer-motion@13.4.6`), `lenis@1.3.26`. Re-check with
> `npm view <pkg> version` before writing a lockfile.
>
> Browser-support statements below are the state at the time of writing — verify against
> caniuse before relying on one, and keep the un-enhanced state usable regardless.

## Timing tokens

Define once, use everywhere. Ad-hoc durations are why sites feel uneven.

```css
:root {
  --d-instant: 80ms;    /* state flips: checkbox, toggle */
  --d-fast:    160ms;   /* hover, focus, small reveals */
  --d-base:    280ms;   /* the default */
  --d-slow:    520ms;   /* entrances, layout shifts */
  --d-deliberate: 900ms;/* hero reveal, page transition */

  --e-out:   cubic-bezier(.16, 1, .3, 1);      /* expo-out: 90% of UI motion */
  --e-inout: cubic-bezier(.65, 0, .35, 1);
  --e-spring: linear(0, .14 4%, .55 12%, .89 20%, 1.03 26%, 1.05 32%, 1, 1);
}
```

`--e-out` (expo-out) is the workhorse: fast start, long settle. Elements should leave
faster than they arrive — exits at `--d-fast`, entrances at `--d-base`/`--d-slow`.

**Never use `ease` or `linear` for UI.** `ease` is the browser default and reads as
unconsidered; `linear` is only correct for continuous motion (marquees, spinners,
scroll-linked progress).

## Choreography

The rule: **one focal element leads, everything else follows in a direction.**

```css
.reveal > * {
  opacity: 0; translate: 0 18px;
  animation: in var(--d-slow) var(--e-out) forwards;
  animation-delay: calc(var(--i, 0) * 70ms);
}
@keyframes in { to { opacity: 1; translate: 0 0; } }
```
```html
<div class="reveal">
  <h2 style="--i:0">…</h2><p style="--i:1">…</p><a style="--i:2">…</a>
</div>
```

Stagger interval: **60-90ms**. Below 50ms it reads as simultaneous; above 120ms it reads
as slow. Cap total choreography at ~600ms — past that, users start scrolling through it.

Animate `opacity`, `translate`, `scale`, `rotate`, `filter`. Never animate `width`,
`height`, `top`, `left`, `margin` — they trigger layout on every frame.

## Reduced motion — the correct shape

Do not delete the animation. Users who set this still need the *information* that
something appeared, and a page whose content never becomes visible is a bug.

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: .01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: .01ms !important;
    scroll-behavior: auto !important;
  }
  /* keep the end state — never leave content at opacity:0 */
  .reveal > * { opacity: 1; translate: none; }
}
```
Test it: DevTools → Rendering → Emulate `prefers-reduced-motion`. Every piece of content
must be visible and every interaction must still be legible.

## Scroll reveal — pick the cheapest that works

**1. Pure CSS (no JS)** — Chromium 115+, Firefox 137+; Safari has not shipped it yet, so
the un-animated state must be the usable state:
```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .fade-up { animation: in linear both; animation-timeline: view();
               animation-range: entry 10% cover 35%; }
  }
}
```

**2. IntersectionObserver** — universal, ~10 lines, no dependency. Default choice.
```js
const io = new IntersectionObserver((es) => {
  for (const e of es) if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
}, { rootMargin: '0px 0px -12% 0px', threshold: 0.01 });
document.querySelectorAll('[data-reveal]').forEach(el => io.observe(el));
```
`unobserve` after firing — re-animating on scroll-up is irritating and costs frames.

**3. GSAP ScrollTrigger** (`gsap@3.15.0`) — only when you need scrubbing, pinning, or a
timeline tied to scroll position.
```js
import gsap from 'gsap';
import ScrollTrigger from 'gsap/ScrollTrigger';
gsap.registerPlugin(ScrollTrigger);

if (!matchMedia('(prefers-reduced-motion: reduce)').matches) {
  gsap.to('.panel', {
    xPercent: -100 * (panels.length - 1), ease: 'none',
    scrollTrigger: { trigger: '.rail', pin: true, scrub: 0.8,
                     end: () => '+=' + document.querySelector('.rail').offsetWidth },
  });
}
```
GSAP's core is free under its standard licence; ScrollTrigger became freely available
with GSAP 3.13 — confirm the current licence terms for commercial use before shipping.

## Motion (Framer Motion) — `motion@13.4.6`

The package was renamed from `framer-motion` to `motion`; both publish the same version
line. New code should import from `motion/react`.

Verified against the installed 13.4.6 package on 2026-09-30: the `./react` export exists,
and `useReducedMotion`, `LazyMotion`, `domAnimation`, `whileInView` and `staggerChildren`
are all present. It also ships a `motion/three` entry point for animating R3F scenes with
the same variant API.

```tsx
import { motion, useReducedMotion } from 'motion/react';

const list = { show: { transition: { staggerChildren: 0.07, delayChildren: 0.1 } } };
const item = { hidden: { opacity: 0, y: 18 }, show: { opacity: 1, y: 0,
               transition: { duration: 0.52, ease: [.16, 1, .3, 1] } } };

export function Reveal({ children }) {
  const reduced = useReducedMotion();
  if (reduced) return <div>{children}</div>;
  return (
    <motion.div variants={list} initial="hidden" whileInView="show"
                viewport={{ once: true, margin: '0px 0px -12% 0px' }}>
      {React.Children.map(children, (c) => <motion.div variants={item}>{c}</motion.div>)}
    </motion.div>
  );
}
```
Prefer `LazyMotion` + `domAnimation` to cut the bundle roughly in half if you only use
`animate`/`whileInView`.

## View Transitions — page and state transitions

Same-document transitions are broadly supported in Chromium and Safari 18+; Firefox is
behind. Cross-document needs `@view-transition`. Always feature-detect.

```js
function update(fn) {
  if (!document.startViewTransition ||
      matchMedia('(prefers-reduced-motion: reduce)').matches) return fn();
  document.startViewTransition(fn);
}
```
```css
::view-transition-old(root) { animation: fade var(--d-fast) var(--e-out) both reverse; }
::view-transition-new(root) { animation: fade var(--d-base) var(--e-out) both; }
.card-img { view-transition-name: hero-img; }   /* morphs between routes */
```
Only one element per page may hold a given `view-transition-name`, or the transition
silently aborts.

## Micro-interactions that carry weight

| Interaction | Spec |
|---|---|
| Button press | `scale: .975` at `--d-instant`, release on `--e-out`. Feels mechanical. |
| Hover on a link | animate a `background-size` underline from 0→100%, `--d-fast`. Not `text-decoration`. |
| Focus ring | `outline: 2px solid var(--accent); outline-offset: 3px` — animate the offset, not the colour. |
| Loading | skeleton matched to the real content's shape, shimmer at `--d-deliberate` `linear`. Never a centred spinner on a full page. |
| Number counters | ease the value with `--e-out`, tabular numerals, stop at the real figure. |
| Marquee | `linear`, duplicated track, `animation-play-state: paused` on hover. |
| Success | one short spring (`--e-spring`), then still. Never loop a success state. |
| Error | 2-cycle shake, 6px, `--d-fast`. Colour alone is not enough. |

## Rules

1. One motion idea per page. Scroll-scrub *or* stagger-reveal, not both everywhere.
2. Nothing animates on load above the fold except the hero choreography — content must
   be readable the instant it paints.
3. Interruptible: a hover-out mid-animation reverses from the current value, never snaps.
4. Frame-rate independent: damp with `dt`, or use CSS. A fixed `lerp(0.05)` runs at
   double speed on a 120 Hz display.
5. Nothing loops forever in the viewport except a marquee or a deliberate ambient effect.
   Looping motion near text destroys readability.
6. If a reviewer notices the animation before the content, it is too much.

## Related

- `design-gate` — its audit fails a page with no reduced-motion handling.
- `web-3d` — scroll-driven camera work and the 3D depth layer.
