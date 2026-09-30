# Token System

## Why OKLCH

`oklch(L C H)` is perceptually uniform: holding L constant keeps perceived brightness
constant across hues, so a palette derived by rotating H stays balanced. Hex and HSL do
not — HSL blue at 50% lightness looks far darker than HSL yellow at 50%.

Baseline browser support is broad (Chrome 111+, Safari 15.4+, Firefox 113+). For anything
that must render in older engines, supply a hex fallback before the oklch declaration:

```css
:root { --accent: #c2410c; --accent: oklch(56% 0.16 42); }
```

## The derivation

Choose **one** hue (`--brand-h`) and **one** accent hue, 30-180° away. Derive everything:

```css
:root {
  --brand-h: 42;
  --accent-h: 250;

  /* light */
  --bg:        oklch(97.5% 0.008 var(--brand-h));
  --surface:   oklch(99.5% 0.004 var(--brand-h));
  --surface-2: oklch(94%   0.012 var(--brand-h));
  --hairline:  oklch(88%   0.014 var(--brand-h));
  --ink:       oklch(21%   0.028 var(--brand-h));
  --ink-muted: oklch(48%   0.020 var(--brand-h));
  --accent:    oklch(56%   0.190 var(--accent-h));
  --accent-ink: oklch(98%  0.010 var(--accent-h));
}

@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg:        oklch(14%   0.018 var(--brand-h));
    --surface:   oklch(18%   0.022 var(--brand-h));
    --surface-2: oklch(23%   0.026 var(--brand-h));
    --hairline:  oklch(30%   0.024 var(--brand-h));
    --ink:       oklch(95%   0.010 var(--brand-h));
    --ink-muted: oklch(70%   0.016 var(--brand-h));
    --accent:    oklch(72%   0.170 var(--accent-h));  /* raise L in dark */
    --accent-ink: oklch(16%  0.030 var(--accent-h));
  }
}
:root[data-theme="dark"] { /* repeat the dark block for the manual toggle */ }

body { background: var(--bg); color: var(--ink); }
```

**Dark-mode rules:** never pure `#000` (halation on OLED, kills depth). Never invert —
raise surfaces by +4-5% L *and* keep chroma, so dark surfaces read as tinted, not gray.
Accents need higher L and slightly lower C in dark to hit contrast without glowing.

## Type scale

Pick a ratio and generate. Don't hand-pick sizes.

| Ratio | Feel | Use |
|---|---|---|
| 1.2 (minor third) | calm, dense | dashboards, docs, data |
| 1.333 (perfect fourth) | balanced | most marketing sites |
| 1.5 (perfect fifth) | dramatic | editorial, portfolios |
| 1.618 (golden) | very dramatic | single-purpose pages |

```css
:root {
  --r: 1.333;
  --t-0:  1rem;                                   /* body */
  --t--1: calc(var(--t-0) / var(--r));            /* caption */
  --t-1:  calc(var(--t-0) * var(--r));
  --t-2:  calc(var(--t-1) * var(--r));
  --t-3:  calc(var(--t-2) * var(--r));
  --t-4:  calc(var(--t-3) * var(--r));            /* display */
}
h1 { font-size: clamp(var(--t-3), 8vw, var(--t-4)); line-height: 0.95; letter-spacing: -0.025em; }
p  { font-size: var(--t-0); line-height: 1.6; max-width: 68ch; }
```

**Display must be ≥ 4× body.** Timid type is the most common cause of a page reading as
generic even when the colors are right.

Tracking: `-0.02em to -0.04em` above 48px, `0` at body, `+0.02em to +0.08em` for
uppercase labels and mono captions.

## Spacing

One scale, geometric, and **use the extremes**. The generic look comes from only ever
using steps 3-5.

```css
:root {
  --s-1: 0.25rem; --s-2: 0.5rem;  --s-3: 0.75rem; --s-4: 1rem;
  --s-5: 1.5rem;  --s-6: 2rem;    --s-7: 3rem;    --s-8: 4.5rem;
  --s-9: 7rem;    --s-10: 11rem;
}
```

Section padding should reach `--s-9`/`--s-10` at desktop. Tight groups should use `--s-1`.

## Elevation

```css
/* two treatments, that is all */
.flat     { background: var(--surface); border: 1px solid var(--hairline); }
.raised   { background: var(--surface);
            box-shadow: 0 1px 2px oklch(20% 0.02 var(--brand-h) / 0.06),
                        0 12px 32px -8px oklch(20% 0.02 var(--brand-h) / 0.14); }
```

Shadows are tinted with the brand hue, never `rgb(0 0 0 / x)` — black shadows read muddy.

## Texture

A page with correct tokens and no texture still reads flat. Add exactly one:

```css
/* film grain — cheap, works everywhere */
.grain::after {
  content: ""; position: fixed; inset: 0; pointer-events: none; z-index: 60;
  opacity: 0.045; mix-blend-mode: overlay;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
}
@media (prefers-reduced-motion: no-preference) { /* animate grain position if desired */ }
```

Alternatives: hairline grid overlay, halftone dots, a single duotoned photograph,
or a WebGL gradient mesh (see `web-3d`).
