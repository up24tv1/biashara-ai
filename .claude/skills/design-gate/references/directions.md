# Committed Art Directions

Pick one. Commit fully. A half-committed direction reads as generic — the failure mode is
blending three of these into mush.

Each entry gives: what it's for, type, color, the depth move, and the rule-break.

---

## 1. Swiss Editorial + Grain
**For:** consultancies, B2B services, agencies, anything selling judgment.
- **Type:** Söhne / Neue Haas Grotesk / *free:* Inter Tight or Archivo as display, 900 weight, tight tracking (-0.03em). Body: Inter 400, 17px, 1.6.
- **Color:** paper `oklch(97% 0.005 85)`, ink `oklch(18% 0.01 260)`, one accent — signal red `oklch(58% 0.21 25)`.
- **Depth:** SVG/canvas film grain overlay at 4-6% opacity + one oversized numeral or letterform bled off-canvas.
- **Break:** headline runs off the right edge. Baseline grid visible as hairlines.

## 2. Brutalist Data
**For:** dev tools, dashboards, technical products, anything for engineers.
- **Type:** monospace everywhere — JetBrains Mono / Berkeley Mono / *free:* Geist Mono, IBM Plex Mono. Display at 700, body 400.
- **Color:** true `#000`/`#fff`, one terminal accent `oklch(80% 0.19 135)` green or `oklch(72% 0.19 55)` amber. Borders `1px solid currentColor`, never gray.
- **Depth:** dense information as texture. ASCII/box-drawing dividers. Live-updating numbers.
- **Break:** zero border-radius, zero shadow. Visible 1px grid. Hard corners are the statement.

## 3. Soft Editorial Serif
**For:** health, wellness, coaching, premium consumer, anything trust-led.
- **Type:** display serif with high contrast — Canela / Editorial New / *free:* Instrument Serif, Fraunces (opsz axis), Newsreader. Body: a humanist sans at 400.
- **Color:** warm neutral ground `oklch(95% 0.015 75)`, deep ink `oklch(25% 0.03 40)`, accent terracotta or sage.
- **Depth:** large duotone photography, soft vignette, generous negative space as a feature.
- **Break:** one line of the headline in italic at 1.4× the rest.

## 4. Dark Chrome / Liquid Metal
**For:** fintech, AI products, crypto, premium SaaS.
- **Type:** geometric sans, tight — Aeonik / Neue Montreal / *free:* Geist, Satoshi, Onest. Display 600, tracking -0.04em.
- **Color:** near-black tinted to brand hue `oklch(14% 0.02 265)`; surfaces raise by +4% L and +0.01 C, never pure gray. Accent: one iridescent gradient used **only** on a 3D surface, never on text.
- **Depth:** **required** — R3F metallic object with env map, or a shader gradient mesh. See `web-3d/references/three-recipes.md` §Chrome Blob.
- **Break:** the 3D object overlaps and occludes the headline.

## 5. Neo-Retro Print
**For:** food, events, music, local business, culture.
- **Type:** condensed display — Druk / *free:* Anton, Archivo Black, Bebas Neue. Paired with a warm slab or mono for body.
- **Color:** limited 4-ink palette, halftone. Off-white stock, no pure white.
- **Depth:** halftone dot pattern, misregistration offset (2px hue-shifted duplicate), paper texture.
- **Break:** type stacked and locked up as a poster block, filling the viewport.

## 6. Spatial / Bento Depth
**For:** product feature pages, mobile app marketing, hardware.
- **Type:** SF Pro / *free:* Inter Display tight, 600. Numerals tabular.
- **Color:** light ground, soft tinted card surfaces, per-card hue accents at low chroma.
- **Depth:** bento grid where cards have **different** heights and one card contains a live 3D or video element. `perspective` on hover tilt.
- **Break:** one bento cell spans 2×2 and breaks the gutter.

## 7. Terminal Luxe
**For:** security, infra, quant, "for serious people" positioning.
- **Type:** mono display + high-contrast serif body. Unexpected pairing is the point.
- **Color:** ink black, bone white, single oxidized accent (copper `oklch(62% 0.12 55)`).
- **Depth:** scanline overlay, CRT curvature on one element, typewriter reveal.
- **Break:** a long single-column measure (68ch) in serif on black.

## 8. Organic Shader Field
**For:** creative studios, portfolios, music, art, experimental.
- **Type:** one weird display face, one neutral body. The face carries the identity.
- **Color:** derived *from* the shader — sample the shader's palette for UI tokens so they can't clash.
- **Depth:** **required** — full-viewport fragment shader (curl noise / domain-warped FBM). See `web-3d/references/shaders.md`.
- **Break:** UI floats over the shader with no card, no scrim — relies on the shader being dark enough.

## 9. Clay / Physical UI
**For:** kids, education, games, playful consumer.
- **Type:** rounded geometric — Nunito, Bricolage Grotesque, Gilroy-alike. Heavy weights.
- **Color:** desaturated pastels at high lightness with *matching* dark shadow hue (never gray shadow).
- **Depth:** dual inset/outset shadows, 3D extruded icons (R3F, `MeshTransmissionMaterial` or matcap).
- **Break:** elements rotate 2-4° off axis, overlapping.

## 10. Archive / Museum
**For:** long-form content, research, publishing, non-profits, DRC News-type editorial.
- **Type:** a text face designed for reading — Source Serif, Literata, Spectral. Display is the same face, larger.
- **Color:** paper, ink, and a single archival red for marks. No third color.
- **Depth:** marginalia, footnotes, figure numbers, hairline rules, drop caps.
- **Break:** two-column asymmetric measure with images breaking into the margin.

## 11. Kinetic Type
**For:** launches, campaigns, single-purpose pages, hype.
- **Type:** variable font, animated along its weight/width axes on scroll.
- **Color:** two colors, maximum contrast, inverted on scroll.
- **Depth:** type *is* the depth — scroll-scrubbed 3D extrusion or per-glyph transform.
- **Break:** no images at all. Type only.

## 12. Warm Utilitarian
**For:** logistics, trades, concrete/construction, field ops, El Shaddai Bukasa Express-type operations.
- **Type:** industrial sans — Roboto Condensed is *acceptable* here; better: Archivo, Barlow Condensed. Tabular numerals mandatory.
- **Color:** hi-vis safety accent `oklch(80% 0.18 85)` on warm concrete gray `oklch(72% 0.01 75)`; ink near-black.
- **Depth:** photographic — real equipment/site photography, duotoned to the palette. Stenciled numerals.
- **Break:** data tables treated as the hero, not hidden below the fold.

---

## Pairing rule

One direction per product. If a dashboard and a marketing site share a brand, use the same
type and color tokens with a different depth strategy — not a different direction.

## Free-font sources

Google Fonts (CDN allowed in artifacts), Fontshare (Satoshi, Bricolage), Vercel Geist,
Uncut.wtf. Verify a face is actually on the CDN before referencing it — a missing font
silently falls back to system sans and undoes the direction.
