# Tier 0 and 1 — depth with no WebGL

Most pages need one of these, not three.js. They cost nothing, never fail, and work as
the fallback layer underneath any WebGL enhancement.

## 1. Card tilt (correct version)

The common version is broken: it forgets `transform-style` and rotates a flat plane.

```html
<div class="tilt"><div class="tilt__inner">…</div></div>
```
```css
.tilt { perspective: 900px; }
.tilt__inner {
  transform-style: preserve-3d;
  transform: rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg)) translateZ(0);
  transition: transform .5s cubic-bezier(.16,1,.3,1);
  will-change: transform;
}
.tilt:hover .tilt__inner { transition-duration: .08s; }   /* fast in, slow out */
/* children can sit at real depth */
.tilt__inner > .badge { transform: translateZ(42px); }
@media (prefers-reduced-motion: reduce) { .tilt__inner { transform: none !important; } }
```
```js
document.querySelectorAll('.tilt').forEach(el => {
  const inner = el.querySelector('.tilt__inner');
  el.addEventListener('pointermove', e => {
    const r = el.getBoundingClientRect();
    const x = (e.clientX - r.left) / r.width  - 0.5;
    const y = (e.clientY - r.top)  / r.height - 0.5;
    inner.style.setProperty('--ry', `${x * 14}deg`);
    inner.style.setProperty('--rx', `${-y * 14}deg`);
  }, { passive: true });
  el.addEventListener('pointerleave', () => {
    inner.style.setProperty('--rx', '0deg'); inner.style.setProperty('--ry', '0deg');
  });
});
```
Cap rotation at ~14°. Beyond that it reads as a gimmick. Only use on pointer devices:
guard with `matchMedia('(hover: hover)')`.

## 2. Scroll-linked parallax with zero JS

Scroll-driven animations are supported in Chromium 115+ and Firefox 137+; Safari has not
shipped them as of this writing — so keep the static state usable and treat it as
progressive enhancement.

```css
@supports (animation-timeline: view()) {
  @media (prefers-reduced-motion: no-preference) {
    .layer-back  { animation: rise linear both; animation-timeline: view(); animation-range: entry 0% cover 60%; }
    .layer-front { animation: rise linear both; animation-timeline: view(); animation-range: entry 0% cover 40%; }
    @keyframes rise { from { transform: translateY(14%) scale(1.06); opacity: .0; }
                      to   { transform: translateY(0)   scale(1);    opacity: 1; } }
  }
}
```
For Safari parity, drive the same custom properties with GSAP ScrollTrigger — see
`motion-system`.

## 3. Canvas 2D particle field (~40 lines, tier 1)

Cheaper than WebGL and often better-looking at low densities, because you get real
antialiasing for free.

```js
const c = document.getElementById('fx'), x = c.getContext('2d', { alpha: true });
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
let dots = [], w, h, dpr = Math.min(devicePixelRatio, 2), raf;

function init() {
  w = c.width = innerWidth * dpr; h = c.height = innerHeight * dpr;
  c.style.width = innerWidth + 'px'; c.style.height = innerHeight + 'px';
  const n = Math.min(160, Math.round(innerWidth / 9));   // density scales with viewport
  dots = Array.from({ length: n }, () => ({
    x: Math.random() * w, y: Math.random() * h,
    vx: (Math.random() - .5) * .18 * dpr, vy: (Math.random() - .5) * .18 * dpr,
    r: (Math.random() * 1.4 + .35) * dpr,
  }));
}
function draw() {
  x.clearRect(0, 0, w, h);
  x.fillStyle = 'rgba(216,201,168,.55)';
  for (const d of dots) {
    d.x = (d.x + d.vx + w) % w; d.y = (d.y + d.vy + h) % h;
    x.beginPath(); x.arc(d.x, d.y, d.r, 0, 6.283); x.fill();
  }
  raf = requestAnimationFrame(draw);
}
addEventListener('resize', init, { passive: true });
init();
reduced ? draw() && cancelAnimationFrame(raf) : draw();
```
Skip connecting lines between particles — the "constellation" effect is as dated as the
purple gradient.

## 4. Layered depth without motion

Depth is mostly occlusion and scale, not animation:

```css
.stack > * { grid-area: 1 / 1; }            /* overlap in a single grid cell */
.stack .plate  { transform: translate(-3%, 4%) rotate(-2.5deg); filter: saturate(.85); }
.stack .plate2 { transform: translate(3%, -2%) rotate(1.5deg); }
.stack .front  { box-shadow: 0 24px 60px -18px oklch(20% .02 42 / .35); }
```
Three overlapping, slightly rotated plates with one tinted shadow reads as more designed
than any amount of `backdrop-blur`.

## 5. Duotone photography

Turns stock or generated imagery into something that belongs to the palette.

```css
.duo { position: relative; isolation: isolate; }
.duo img { filter: grayscale(1) contrast(1.15); }
.duo::after {
  content: ""; position: absolute; inset: 0; z-index: 1;
  background: linear-gradient(150deg, var(--accent), var(--ink));
  mix-blend-mode: color;
}
```

## 6. Custom cursor (pointer devices only)

```css
@media (hover: hover) and (pointer: fine) {
  .cursor { position: fixed; top: 0; left: 0; width: 28px; height: 28px; border-radius: 50%;
            border: 1px solid var(--ink); pointer-events: none; z-index: 99;
            translate: -50% -50%; transition: scale .2s, opacity .2s; mix-blend-mode: difference; }
  a:hover ~ .cursor, button:hover ~ .cursor { scale: 2.2; }
}
```
Never hide the native cursor without a replacement that tracks at full frame rate — a
laggy custom cursor is worse than none. Keep the OS cursor visible on any form control.
