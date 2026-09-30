# Anti-Slop: why each ban exists, and the fix in code

## 1. The purple-blue gradient

It is the default because it is the safest possible choice in every LLM's training
distribution. Safety is the problem — it signals "no one decided anything."

```css
/* BAD */
background: linear-gradient(to right, #8b5cf6, #3b82f6);

/* GOOD — one hue family, chroma does the work, not hue rotation */
:root {
  --brand-h: 25;               /* pick once, per project */
  --bg:      oklch(97% 0.008 var(--brand-h));
  --surface: oklch(99% 0.004 var(--brand-h));
  --ink:     oklch(22% 0.03  var(--brand-h));
  --accent:  oklch(56% 0.20  var(--brand-h));
}
.hero { background: linear-gradient(170deg,
        oklch(97% 0.008 var(--brand-h)),
        oklch(93% 0.02  calc(var(--brand-h) + 12))); }
```

Gradient rules: stay within 20° of hue, move lightness more than hue, use an off-axis
angle (170deg, not 90deg/to-right).

## 2. Inter as the display face

Inter is an excellent UI face and a characterless display face. Using it at 72px/700 is
the single strongest "AI built this" signal.

```html
<!-- BAD -->
<h1 class="text-6xl font-bold">Elevate Your Workflow</h1>

<!-- GOOD — display face with a voice, real tracking, real size -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500&display=swap">
<h1 style="font-family:'Instrument Serif',serif; font-size:clamp(3rem,9vw,7.5rem);
           line-height:0.92; letter-spacing:-0.02em; font-weight:400">
  Freight moves<br><em>or it doesn't.</em>
</h1>
```

Large type needs negative tracking. Small type needs positive. Inter at 400 for body is fine.

## 3. The centered hero triptych

`h1` + subtitle + two buttons, all centered, is the wireframe every model reaches for.

**Fix:** put the headline on a 7-column span starting at column 2, put the CTA inline with
the last line of the headline, and let something visual occupy columns 9-13 and bleed off
the right edge. One CTA. The verb names the outcome ("See the 30-day recovery plan"), not
"Get Started".

## 4. Three identical feature cards

```jsx
/* BAD */
{features.map(f => (
  <div className="rounded-2xl shadow-lg p-6 bg-white">
    <div className="w-12 h-12 rounded-xl bg-purple-100 grid place-items-center">{f.emoji}</div>
    <h3 className="font-bold mt-4">{f.title}</h3><p>{f.body}</p>
  </div>
))}

/* GOOD — varied weight, one card dominant, no uniform shadow */
<div className="grid grid-cols-1 md:grid-cols-12 gap-px bg-[--hairline]">
  <article className="md:col-span-7 md:row-span-2 bg-[--surface] p-10">
    <p className="font-mono text-xs tracking-widest opacity-60">01</p>
    <h3 className="mt-6 text-4xl leading-[0.95]">{f0.title}</h3>
    <p className="mt-4 max-w-[42ch] opacity-70">{f0.body}</p>
    {/* this one carries the 3D / image */}
  </article>
  <article className="md:col-span-5 bg-[--surface] p-8">…</article>
  <article className="md:col-span-5 bg-[--surface] p-8">…</article>
</div>
```

Hairline `gap-px` over a background color beats shadows and gives a Swiss grid for free.

## 5. `rounded-2xl shadow-lg` everywhere

Uniform elevation flattens hierarchy — if everything floats, nothing does.

Rule: **two** surface treatments per page, maximum. E.g. `flat + hairline border` for
content, and `elevated` reserved for exactly one thing (a modal, or the one dominant card).
Radius: pick 0, 4px, or 24px+. The 8-16px range is the "no decision" zone.

## 6. Gradient text headlines

`bg-clip-text text-transparent` on an h1 destroys legibility and is pure 2021 template.
If the headline feels weak, the *typeface* is weak. Solid ink, larger size, tighter leading.

## 7. Emoji as icons

Emoji render differently per OS, break the type system, and cannot be recolored.
Use one set with a consistent stroke — Lucide, Phosphor, Radix Icons — or ship no icons.
Numerals (01, 02, 03) in mono are almost always better than icons anyway.

## 8. Uniform section rhythm

`py-20` on eight sections in a row produces a scroll with no dynamics.

```
section 1 (hero)     min-h-[88vh]
section 2            py-16, full-bleed background, edge to edge
section 3            py-32, narrow measure, centered
section 4            py-16, asymmetric split, sticky left column
section 5 (CTA)      py-24, inverted colors
```

Vary the *container* too: alternate `max-w-6xl`, full-bleed, and `max-w-[68ch]`.

## 9. Fake social proof

Invented testimonials, ★★★★★ rows, and stock-photo avatars are both slop and a
credibility risk. If real quotes don't exist, ship the section as a single factual
claim with a number, or omit it. Never fabricate a customer.

## 10. Slop copy

Banned openers and phrases: *Elevate, Seamlessly, Unlock the power of, Transform your,
Supercharge, Take X to the next level, In today's fast-paced world, Revolutionize,
Empower, Effortlessly, game-changer, cutting-edge, robust solution.*

Replace with the specific mechanism and a number:
- ❌ "Transform your restaurant operations with AI-powered automation"
- ✅ "Answers the phone at 7pm. Books the table. Texts the confirmation. $2,400/mo of
  front-of-house labor you stop paying for."

## 11. Placeholder content

Lorem ipsum and gray boxes make a page impossible to judge. Generate real-shaped content:
Pollinations.ai for imagery (free, no key), Canva MCP, or an R3F object instead of a
hero image. Copy should be the real pitch even in a prototype.

## 12. Untouched shadcn/ui

shadcn defaults are deliberately neutral — they are a starting point, not a design.
Before using it, override in `globals.css`: `--radius`, `--border`, shadow scale, and
the font variables. Then restyle `Button` variants to the direction.
