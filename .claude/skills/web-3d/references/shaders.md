# Shaders that earn their place

Tier 2: full-viewport WebGL with no geometry and no 3D library. ~3 KB with `ogl`, or
~40 lines of raw WebGL. This is the cheapest way to make a page stop looking flat.

> **Verified 2026-09-30**: every fragment shader below was compiled and linked in headless
> Chromium (WebGL2 / SwiftShader) with zero compile or link errors.

## 1. Domain-warped FBM gradient mesh

The "Organic Shader Field" and "Dark Chrome" directions live on this. It replaces the
banned CSS gradient with something that moves, has grain, and can't look like a template.

```glsl
#version 300 es
precision highp float;

uniform vec2  uRes;
uniform float uTime;
uniform vec3  uA;     // deep shadow colour
uniform vec3  uB;     // mid
uniform vec3  uC;     // highlight / accent
out vec4 fragColor;

// -- value noise -------------------------------------------------------------
vec2 hash2(vec2 p){
  p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
  return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}
float noise(vec2 p){
  vec2 i = floor(p), f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);          // smoothstep
  return mix(mix(dot(hash2(i + vec2(0,0)), f - vec2(0,0)),
                 dot(hash2(i + vec2(1,0)), f - vec2(1,0)), u.x),
             mix(dot(hash2(i + vec2(0,1)), f - vec2(0,1)),
                 dot(hash2(i + vec2(1,1)), f - vec2(1,1)), u.x), u.y);
}
float fbm(vec2 p){
  float v = 0.0, a = 0.5;
  mat2 rot = mat2(0.80, 0.60, -0.60, 0.80);  // rotate each octave to kill axis artefacts
  for (int i = 0; i < 5; i++){ v += a * noise(p); p = rot * p * 2.02; a *= 0.5; }
  return v;
}

void main(){
  // aspect-correct, origin-centred
  vec2 uv = (gl_FragCoord.xy * 2.0 - uRes) / min(uRes.x, uRes.y);
  float t = uTime * 0.06;

  // domain warping: noise fed into noise. This is what makes it read as "liquid"
  // rather than "clouds" — the single most important line in the shader.
  vec2 q = vec2(fbm(uv + vec2(0.0, t)), fbm(uv + vec2(5.2, 1.3) - t));
  vec2 r = vec2(fbm(uv + 4.0 * q + vec2(1.7, 9.2) + t * 0.7),
                fbm(uv + 4.0 * q + vec2(8.3, 2.8) - t * 0.5));
  float f = fbm(uv + 4.0 * r);

  vec3 col = mix(uA, uB, clamp(f * f * 2.4, 0.0, 1.0));
  col = mix(col, uC, clamp(length(q) * 0.85, 0.0, 1.0));
  col = mix(col, uC * 1.15, clamp(r.x * 0.5, 0.0, 1.0));

  // grain — without this it looks like a 2015 mesh gradient
  float g = fract(sin(dot(gl_FragCoord.xy, vec2(12.9898, 78.233))) * 43758.5453);
  col += (g - 0.5) * 0.035;

  // vignette keeps UI legible over the field
  col *= 1.0 - 0.35 * length(uv * vec2(0.55, 0.75));

  fragColor = vec4(col, 1.0);
}
```

**Token discipline:** sample `uA/uB/uC` *from* your OKLCH tokens so the shader can never
clash with the UI. Convert once at build time, or read the computed custom property:
```js
const css = getComputedStyle(document.documentElement);
// store plain "r,g,b" floats alongside the oklch tokens to avoid a colour-space round trip
```

### Minimal `ogl` host (tier 2, ~3 KB)

```js
import { Renderer, Triangle, Program, Mesh } from 'ogl';   // ogl@1.0.11

const renderer = new Renderer({ alpha: false, dpr: Math.min(devicePixelRatio, 2) });
const gl = renderer.gl;
document.getElementById('bg').appendChild(gl.canvas);

const program = new Program(gl, {
  vertex: `#version 300 es
    in vec2 position;
    void main(){ gl_Position = vec4(position, 0.0, 1.0); }`,
  fragment: FRAG,            // the GLSL above
  uniforms: {
    uRes:  { value: [1, 1] },
    uTime: { value: 0 },
    uA: { value: [0.055, 0.055, 0.075] },
    uB: { value: [0.180, 0.150, 0.230] },
    uC: { value: [0.850, 0.560, 0.270] },
  },
});
const mesh = new Mesh(gl, { geometry: new Triangle(gl), program });

function resize(){
  renderer.setSize(innerWidth, innerHeight);
  program.uniforms.uRes.value = [gl.canvas.width, gl.canvas.height];
}
addEventListener('resize', resize, { passive: true }); resize();

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
function loop(t){ program.uniforms.uTime.value = t * 0.001; renderer.render({ scene: mesh });
                  if (!reduced) requestAnimationFrame(loop); }
requestAnimationFrame(loop);   // reduced-motion still gets exactly one rendered frame
```

A `Triangle` (one oversized tri) beats a quad: no diagonal seam, one fewer vertex, and no
overdraw at the centre.

---

## 2. Image displacement on hover

Turns a flat portfolio grid into something that feels physical. Works on any `<img>`.

```glsl
#version 300 es
precision highp float;
uniform sampler2D uTex;
uniform float uHover;      // 0..1, eased in JS
uniform vec2  uMouse;      // 0..1 within the element
in  vec2 vUv;
out vec4 fragColor;

void main(){
  vec2 uv = vUv;
  float d = distance(uv, uMouse);
  float ripple = smoothstep(0.45, 0.0, d) * uHover;

  // per-channel offset = chromatic aberration at the displaced edge
  vec2 dir = normalize(uv - uMouse + 1e-5) * ripple * 0.035;
  float r = texture(uTex, uv - dir * 1.00).r;
  float g = texture(uTex, uv - dir * 0.85).g;
  float b = texture(uTex, uv - dir * 0.70).b;

  fragColor = vec4(r, g, b, 1.0);
}
```
Ease `uHover` in JS (`u += (target - u) * 0.08`) — never snap it. An instant 0→1 reads
as a glitch, not an interaction.

---

## 3. Animated grain overlay (no geometry, no library)

When a page needs texture and nothing else, this is 20 lines of raw WebGL over the
whole viewport at `mix-blend-mode: overlay`.

```glsl
#version 300 es
precision highp float;
uniform vec2 uRes; uniform float uTime;
out vec4 fragColor;
void main(){
  vec2 p = gl_FragCoord.xy;
  float n = fract(sin(dot(p + uTime * 60.0, vec2(12.9898, 78.233))) * 43758.5453);
  fragColor = vec4(vec3(n), 0.055);
}
```
If that's the only effect you need, use the SVG `feTurbulence` version in
`design-gate/references/tokens.md` instead — zero JS, zero GL context.

---

## Shader rules

1. **Precision**: `highp` in fragment shaders. `mediump` banding shows badly in gradients.
2. **No branching in hot loops** — mobile GPUs serialise divergent branches.
3. **Octaves**: 5 is the ceiling for a full-viewport FBM at 60fps on mid-range mobile.
   Drop to 3 when `hardwareConcurrency <= 4`.
4. **Always grain.** A clean gradient reads as CSS. Grain reads as film.
5. **Rotate octaves** (`mat2` above). Un-rotated FBM shows visible axis-aligned streaks.
6. **Vignette or scrim** wherever text overlays the field — otherwise contrast fails at
   some frames and you can't test for it statically.
7. **WebGL1 fallback**: if you must support it, drop `#version 300 es`, swap `in`/`out`
   for `varying`/`attribute`, use `gl_FragColor`, and `texture2D` instead of `texture`.
