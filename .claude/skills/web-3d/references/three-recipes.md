# Vanilla three.js recipes (CDN importmap)

Works in a single HTML file, a published artifact, or a Cloudflare Worker-served page —
no build step. Pinned to `three@0.186.1`.

> **Verified 2026-09-30** against `three@0.186.1` source, and the Chrome Blob recipe was
> executed in headless Chromium (WebGL2/SwiftShader): 1 draw call, 21,780 triangles,
> custom vertex shader compiles, disposal clean, zero console output.
>
> **API drift warning.** three.js makes breaking changes on a roughly monthly cadence.
> Pin the version and check the signature against that exact tag if something throws.
> Confirmed at 0.186.1: `new RoomEnvironment()` takes **no** renderer argument (changed
> ~r167); `PMREMGenerator.fromScene(scene, sigma, near, far)`; `TextGeometry` uses
> **`depth`**, not `height`; **`THREE.Clock` is deprecated — use `THREE.Timer`**
> (`timer.update(ts)` then `timer.getElapsed()` / `getDelta()`).
>
> **CDN may be blocked.** Some sandboxes and corporate networks block
> `cdn.jsdelivr.net` / `unpkg.com` (this Claude cloud container does). If the importmap
> fails to resolve, `npm i three@0.186.1` and point the importmap at
> `./node_modules/three/build/three.module.js` and `./node_modules/three/examples/jsm/`.
> Everything below works unchanged either way.

## Boilerplate + disposal (start every scene from this)

```html
<script type="importmap">
{ "imports": {
  "three": "https://cdn.jsdelivr.net/npm/three@0.186.1/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/"
}}
</script>
<canvas id="gl" aria-hidden="true"></canvas>
<style>
  #gl { position: fixed; inset: 0; width: 100%; height: 100%; display: block; z-index: 0; }
  /* the typographic hero sits above and paints first */
  .hero { position: relative; z-index: 1; }
</style>

<script type="module">
import * as THREE from 'three';

const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const weak = !self.WebGL2RenderingContext || (navigator.hardwareConcurrency ?? 8) <= 4;

const canvas = document.getElementById('gl');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: !weak, alpha: true,
                                           powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, weak ? 1.5 : 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;
// colour management and SRGBColorSpace output are the defaults since r152.

const scene  = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);
camera.position.set(0, 0, 6);

function resize() {
  const w = canvas.clientWidth, h = canvas.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize, { passive: true });
resize();

// THREE.Clock is deprecated as of r186 — Timer is the replacement.
// setAnimationLoop passes a timestamp; feed it straight to the timer.
const timer = new THREE.Timer();
function frame(ts) {
  timer.update(ts);
  update(timer.getElapsed());      // update() is defined per recipe below
  renderer.render(scene, camera);
}

// pause when offscreen; render exactly one frame when motion is reduced
const io = new IntersectionObserver(([e]) => {
  if (e.isIntersecting && !reduced) renderer.setAnimationLoop(frame);
  else { renderer.setAnimationLoop(null); if (reduced) frame(performance.now()); }
}, { threshold: 0 });
io.observe(canvas);

// Safari leaks WebGL contexts across route changes without this.
function dispose() {
  renderer.setAnimationLoop(null);
  io.disconnect();
  scene.traverse(o => {
    o.geometry?.dispose();
    const m = o.material;
    if (Array.isArray(m)) m.forEach(x => x.dispose());
    else if (m) { Object.values(m).forEach(v => v?.isTexture && v.dispose()); m.dispose(); }
  });
  renderer.dispose();
}
addEventListener('pagehide', dispose);
</script>
```

---

## 1. Chrome blob — "Dark Chrome / Liquid Metal" direction

A single metallic form with a procedural studio environment. No asset files, no lights,
~2 draw calls. This is the highest ratio of perceived polish to effort in the whole skill.

```js
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
pmrem.dispose();

const blob = new THREE.Mesh(
  new THREE.IcosahedronGeometry(1.6, 32),   // detail 32 = 21,780 tris; detail 64 = 84,500 (over mobile budget)
  new THREE.MeshPhysicalMaterial({
    color: 0xffffff, metalness: 1, roughness: 0.16,
    clearcoat: 1, clearcoatRoughness: 0.08,
    iridescence: 1, iridescenceIOR: 1.6, iridescenceThicknessRange: [120, 520],
  })
);
scene.add(blob);

// displace the surface in the vertex stage — cheaper and smoother than CPU morphing
blob.material.onBeforeCompile = (s) => {
  s.uniforms.uTime = { value: 0 };
  blob.material.userData.u = s.uniforms;
  s.vertexShader = s.vertexShader
    .replace('#include <common>', `#include <common>
      uniform float uTime;
      // cheap 3-octave value-ish noise via sines: no texture, no branches
      float wob(vec3 p){
        return sin(p.x*1.7 + uTime*0.6) * 0.5
             + sin(p.y*2.3 - uTime*0.45) * 0.3
             + sin(p.z*3.1 + uTime*0.8)  * 0.2;
      }`)
    .replace('#include <begin_vertex>', `#include <begin_vertex>
      transformed += normal * wob(position * 1.15) * 0.22;`);
};

function update(t) {
  const u = blob.material.userData.u;
  if (u) u.uTime.value = t;
  blob.rotation.y = t * 0.14;
  blob.rotation.x = Math.sin(t * 0.21) * 0.12;
  // pointer parallax, damped
  camera.position.x += (px * 0.7 - camera.position.x) * 0.045;
  camera.position.y += (py * 0.4 - camera.position.y) * 0.045;
  camera.lookAt(0, 0, 0);
}

let px = 0, py = 0;
addEventListener('pointermove', e => {
  px = (e.clientX / innerWidth) * 2 - 1;
  py = -((e.clientY / innerHeight) * 2 - 1);
}, { passive: true });
```

**Note on displacement:** modifying `transformed` along the original `normal` leaves
normals stale, so lighting is slightly wrong on steep deformations. It is invisible on a
smooth metallic blob. If you displace hard (> 0.4), recompute normals in the shader or use
`flatShading: true` deliberately.

---

## 2. Extruded type — "Kinetic Type" direction

**Prefer SVG extrusion.** `three`'s bundled typeface JSON files live in the GitHub repo's
`examples/fonts/`, which is **not** part of the npm tarball — so a
`cdn.jsdelivr.net/npm/three@.../examples/fonts/...` URL 404s. Verified against the 0.186.1
package: it ships `examples/jsm/` only. Export your real brand wordmark as SVG and extrude
it. Better fidelity, correct letterforms, no extra font pipeline.

```js
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';

new SVGLoader().load('/brand/wordmark.svg', (data) => {
  const group = new THREE.Group();
  const mat = new THREE.MeshPhysicalMaterial({
    color: 0x111114, metalness: 0.9, roughness: 0.25, clearcoat: 1,
  });
  for (const path of data.paths) {
    for (const shape of SVGLoader.createShapes(path)) {
      const geo = new THREE.ExtrudeGeometry(shape, {
        depth: 18, bevelEnabled: true, bevelThickness: 2, bevelSize: 1.4, bevelSegments: 4,
      });
      group.add(new THREE.Mesh(geo, mat));
    }
  }
  // SVG Y axis points down, and units are px — flip and normalise
  group.scale.set(0.01, -0.01, 0.01);
  new THREE.Box3().setFromObject(group)
    .getCenter(group.position).multiplyScalar(-1);
  scene.add(group);
});
```

If you do want the stock typeface route, self-host the JSON: convert a TTF/OTF with
facetype.js (gero3.github.io/facetype.js) and load it from your own origin.

```js
import { FontLoader } from 'three/addons/loaders/FontLoader.js';
import { TextGeometry } from 'three/addons/geometries/TextGeometry.js';

new FontLoader().load('/fonts/brand.typeface.json', (font) => {
  const geo = new TextGeometry('FREIGHT', {
    font, size: 1, depth: 0.35, curveSegments: 12,       // `depth`, not `height` (r163+)
    bevelEnabled: true, bevelThickness: 0.03, bevelSize: 0.02, bevelSegments: 4,
  });
  geo.center();
  scene.add(new THREE.Mesh(geo, new THREE.MeshPhysicalMaterial({
    color: 0x111114, metalness: 0.9, roughness: 0.25, clearcoat: 1,
  })));
});
```

---

## 3. glTF product viewer

```js
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const draco = new DRACOLoader().setDecoderPath(
  'https://cdn.jsdelivr.net/npm/three@0.186.1/examples/jsm/libs/draco/');
const loader = new GLTFLoader().setDRACOLoader(draco);

loader.load('/models/product.glb', (gltf) => {
  const root = gltf.scene;
  // normalise unknown model scale to a 2-unit box
  const box = new THREE.Box3().setFromObject(root);
  const size = box.getSize(new THREE.Vector3()).length();
  root.scale.setScalar(2 / size);
  root.position.sub(box.getCenter(new THREE.Vector3()).multiplyScalar(2 / size));
  scene.add(root);
});

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.enablePan = false;
controls.minDistance = 3; controls.maxDistance = 9;
controls.autoRotate = true; controls.autoRotateSpeed = 0.5;
// update() inside the loop:  controls.update();
```

Compress first — an uncompressed glb will blow the 2 MB budget:
```bash
npx @gltf-transform/cli optimize in.glb out.glb --texture-compress webp --simplify
```

---

## 4. Scroll-driven camera

Pair with `lenis` for smooth scroll. Keep the camera path declarative so it can be tuned
without touching the loop.

```js
import Lenis from 'https://cdn.jsdelivr.net/npm/lenis@1.3.26/dist/lenis.mjs';
const lenis = new Lenis({ autoRaf: false, lerp: 0.09 });

const path = [
  { at: 0.0, pos: [0, 0, 6],     look: [0, 0, 0] },
  { at: 0.5, pos: [2.4, 0.8, 3], look: [0, 0.2, 0] },
  { at: 1.0, pos: [0, 2.6, 2.2], look: [0, 0, -1] },
];
const v = new THREE.Vector3(), l = new THREE.Vector3();

function sampleCamera(p) {
  let i = 0;
  while (i < path.length - 2 && p > path[i + 1].at) i++;
  const a = path[i], b = path[i + 1];
  const k = THREE.MathUtils.smoothstep(p, a.at, b.at);
  v.fromArray(a.pos).lerp(new THREE.Vector3().fromArray(b.pos), k);
  l.fromArray(a.look).lerp(new THREE.Vector3().fromArray(b.look), k);
  camera.position.copy(v);
  camera.lookAt(l);
}

function update(t) {
  lenis.raf(t * 1000);
  const max = document.documentElement.scrollHeight - innerHeight;
  sampleCamera(max > 0 ? THREE.MathUtils.clamp(scrollY / max, 0, 1) : 0);
}
```
When motion is reduced, skip Lenis and jump the camera to the progress value on `scroll`
directly — the page stays usable, it just doesn't glide.

---

## 5. Instanced particle field

30k points, one draw call. Use for "Organic Shader Field" or as a subtle backdrop.

```js
const COUNT = 30000;
const pos = new Float32Array(COUNT * 3);
for (let i = 0; i < COUNT; i++) {
  // even distribution on a shell, not a cube — cubes read as noise
  const r = 3.2 + Math.random() * 1.6;
  const th = Math.random() * Math.PI * 2;
  const ph = Math.acos(2 * Math.random() - 1);
  pos.set([r * Math.sin(ph) * Math.cos(th),
           r * Math.sin(ph) * Math.sin(th),
           r * Math.cos(ph)], i * 3);
}
const geo = new THREE.BufferGeometry();
geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));

const points = new THREE.Points(geo, new THREE.PointsMaterial({
  size: 0.012, color: 0xd8c9a8, transparent: true, opacity: 0.85,
  depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
}));
scene.add(points);

function update(t) { points.rotation.y = t * 0.03; points.rotation.x = t * 0.012; }
```
`depthWrite: false` + additive blending is what stops particle fields looking like dirt.

---

## Fallback pattern

```js
if (weak || !renderer.capabilities.isWebGL2) {
  canvas.remove();
  document.body.classList.add('static-depth');   // tier-0 gradient + grain takes over
}
```
Ship the tier-0 version as the base layer in CSS and *enhance* with WebGL. Then the
fallback is free and always correct.
