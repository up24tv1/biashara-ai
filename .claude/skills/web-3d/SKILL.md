---
name: web-3d
description: "3D and WebGL elements for websites and apps. Use when a page needs depth, a 3D object, a shader background, a particle field, scroll-driven camera motion, an interactive product/hero object, tilt cards, or when asked for 3D, three.js, React Three Fiber, R3F, WebGL, GLSL, shaders, Spline, gradient mesh, glassmorphic 3D, metallic/chrome objects, extruded type, point clouds, or a hero that isn't flat. Also use when a design needs its DEPTH requirement satisfied (see design-gate). Covers vanilla three.js via CDN for static pages/artifacts, R3F for React/Next.js, performance budgets, mobile and reduced-motion fallbacks, and pinned working versions."
---

# Web 3D

Depth is what separates a designed page from a styled one. This skill covers the four
depth tiers, cheapest first — pick the lowest tier that satisfies the design, because
every tier above costs bundle size, battery, and accessibility work.

## Choose the tier

| Tier | Cost | Use when |
|---|---|---|
| **0 — CSS depth** | 0 KB | Tilt cards, parallax layers, `perspective`, blend modes, grain. Most pages stop here. |
| **1 — Canvas 2D / SVG** | ~2 KB | Particle fields, noise, halftone, generative line art. No WebGL context. |
| **2 — Raw WebGL shader** | ~3 KB (`ogl`) or hand-rolled | Full-viewport gradient mesh, liquid backgrounds, displaced images. No geometry needed. |
| **3 — three.js / R3F** | 150 KB+ gz | Actual 3D objects, product views, extruded type, scroll-driven camera, physical materials. |

Do not reach for tier 3 to draw a gradient. Do not fake tier 3 with a video file over 2 MB.

## Pinned versions

Verified against the npm registry on 2026-09-30:

| Package | Version | Note |
|---|---|---|
| `three` | 0.186.1 | API moves between releases — pin it and match docs to the pinned tag |
| `@react-three/fiber` | 9.8.1 | v9 requires React 19 |
| `@react-three/drei` | 10.7.9 | helpers: `Environment`, `Float`, `useScroll`, `MeshTransmissionMaterial` |
| `@react-three/postprocessing` | 3.1.3 | pairs with `postprocessing` 6.39.5 |
| `@splinetool/react-spline` | 4.1.0 | designer-made scenes; heavy — budget the `.splinecode` payload |
| `ogl` | 1.0.11 | minimal WebGL, ideal for tier 2 |
| `lenis` | 1.3.26 | smooth scroll for scroll-driven 3D |
| `gsap` | 3.15.0 | ScrollTrigger; see `motion-system` |

Always `npm view <pkg> version` before writing a lockfile — these move.

## Non-negotiables

Every 3D element ships with all five:

1. **Reduced-motion**: `matchMedia('(prefers-reduced-motion: reduce)')` → render one static
   frame and stop the loop. The static frame must still look designed.
2. **Mobile fallback**: a device with `navigator.hardwareConcurrency <= 4` or no WebGL gets
   a static poster image or the tier-0 version. Test at 375px.
3. **DPR clamp**: `Math.min(devicePixelRatio, 2)`. Never render at 3× on a phone.
4. **Pause offscreen**: `IntersectionObserver` → `renderer.setAnimationLoop(null)`.
5. **Dispose**: geometries, materials, textures, and the renderer on unmount. Leaked
   contexts crash Safari after a few route changes.

## Budgets

| Metric | Budget |
|---|---|
| JS for the 3D layer (gzipped) | ≤ 180 KB, lazy-loaded below the fold or after first paint |
| Draw calls | ≤ 60 |
| Triangles | ≤ 150k desktop / 60k mobile |
| Textures | ≤ 2048², KTX2/Basis where possible |
| glTF payload | ≤ 2 MB, Draco or meshopt compressed |
| Frame budget | 8 ms desktop, 12 ms mobile |
| LCP impact | zero — 3D must never be the LCP element |

Never block first paint on 3D. Render the typographic hero immediately, mount the canvas
after `requestIdleCallback` or on intersection.

## Recipes

Copy-paste, runnable:

- `references/three-recipes.md` — vanilla three.js via importmap CDN (works in a single
  HTML file and in published artifacts): chrome blob with env map, extruded type, glTF
  product viewer, scroll-driven camera, instanced particle field, plus full disposal.
- `references/r3f-recipes.md` — React Three Fiber / Next.js: SSR-safe canvas, lazy mount,
  `MeshTransmissionMaterial` glass, scroll rig, postprocessing stack, perf guards.
- `references/shaders.md` — GLSL that earns its place: domain-warped FBM gradient mesh,
  animated grain, image displacement on hover, chromatic edge. With the `ogl` tier-2 setup.
- `references/css-depth.md` — tier 0 and 1: 3D tilt with correct `transform-style`,
  layered parallax, canvas particle field, grain, halftone, custom cursor.

## Asset sources

- **Models**: Poly Haven (CC0), Sketchfab (filter CC), Quaternius (CC0). Compress with
  `gltf-transform optimize in.glb out.glb --texture-compress webp`.
- **HDRIs / env maps**: Poly Haven. Or skip the file entirely — `RoomEnvironment` from
  three's addons generates a usable studio env procedurally.
- **Matcaps**: free matcap sets render metal and clay convincingly with zero lighting cost.
  Cheapest way to look expensive.
- **Generated textures**: Pollinations.ai (free, no key) for grain, marble, concrete maps.

## Related skills

- `design-gate` — run its audit after adding 3D; it checks the depth requirement.
- `motion-system` — scroll and timeline choreography that drives the camera.
