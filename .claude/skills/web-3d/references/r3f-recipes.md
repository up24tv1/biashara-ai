# React Three Fiber (Next.js / React 19)

```bash
npm i three@0.186.1 @react-three/fiber@9.8.1 @react-three/drei@10.7.9
# optional: @react-three/postprocessing@3.1.3 postprocessing@6.39.5 lenis@1.3.26
```
R3F v9 requires **React 19**. On React 18, pin `@react-three/fiber@8`.

## SSR-safe, lazily mounted canvas

Never import three into the server bundle, and never let 3D block LCP.

```tsx
// components/Scene.tsx  — client only
'use client';
import { Canvas } from '@react-three/fiber';
import { Environment, Float, AdaptiveDpr, AdaptiveEvents, Preload } from '@react-three/drei';
import { Suspense } from 'react';
import Blob from './Blob';

export default function Scene() {
  return (
    <Canvas
      dpr={[1, 2]}                       // never 3x
      gl={{ antialias: true, alpha: true, powerPreference: 'high-performance' }}
      camera={{ position: [0, 0, 6], fov: 35 }}
      frameloop="demand"                 // render only when something changes
      style={{ position: 'absolute', inset: 0 }}
    >
      <Suspense fallback={null}>
        <Environment preset="studio" />  {/* procedural; no HDRI download */}
        <Float speed={1.1} rotationIntensity={0.35} floatIntensity={0.7}>
          <Blob />
        </Float>
        <Preload all />
      </Suspense>
      <AdaptiveDpr pixelated />          {/* drops resolution when fps sags */}
      <AdaptiveEvents />
    </Canvas>
  );
}
```

```tsx
// app/page.tsx
import dynamic from 'next/dynamic';
const Scene = dynamic(() => import('@/components/Scene'), {
  ssr: false,
  loading: () => <div className="scene-poster" aria-hidden />,  // tier-0 gradient + grain
});

export default function Page() {
  return (
    <section className="relative min-h-[88svh]">
      <Scene />
      <h1 className="relative z-10">…</h1>   {/* paints immediately, independent of WebGL */}
    </section>
  );
}
```

`frameloop="demand"` is the single biggest win on a marketing page: the canvas idles at
0% CPU until something invalidates it. Use `frameloop="always"` only for a continuously
animating scene, and pair it with the visibility guard below.

## Reduced motion + visibility, as a hook

```tsx
'use client';
import { useThree, useFrame } from '@react-three/fiber';
import { useEffect, useState } from 'react';

export function useMotionGuard() {
  const [reduced, setReduced] = useState(false);
  const invalidate = useThree((s) => s.invalidate);
  useEffect(() => {
    const mq = matchMedia('(prefers-reduced-motion: reduce)');
    const on = () => { setReduced(mq.matches); invalidate(); };  // still render one frame
    on(); mq.addEventListener('change', on);
    const vis = () => !document.hidden && invalidate();
    document.addEventListener('visibilitychange', vis);
    return () => { mq.removeEventListener('change', on);
                   document.removeEventListener('visibilitychange', vis); };
  }, [invalidate]);
  return reduced;
}

// in a component:
// const reduced = useMotionGuard();
// useFrame((state, dt) => { if (reduced) return; mesh.current.rotation.y += dt * 0.15; });
```

## Glass / transmission material

The convincing version of "glassmorphism" — actual refraction, not `backdrop-blur`.

```tsx
import { MeshTransmissionMaterial } from '@react-three/drei';

<mesh>
  <torusKnotGeometry args={[1, 0.34, 220, 40]} />
  <MeshTransmissionMaterial
    thickness={0.9} roughness={0.08} transmission={1} ior={1.45}
    chromaticAberration={0.06} anisotropy={0.25} distortion={0.35}
    distortionScale={0.4} temporalDistortion={0.12}
    samples={6}          // 4-6 on mobile, 10 desktop; each sample is a full re-render
    resolution={512}     // 256 on mobile
    backside={false}     // backside doubles the cost — only for thick glass
  />
</mesh>
```
Transmission is the most expensive material in the library. Budget it as the *only*
heavy element on the page, and drop `samples` and `resolution` on low-core devices.

## Scroll rig

```tsx
import { ScrollControls, Scroll, useScroll } from '@react-three/drei';
import { useFrame } from '@react-three/fiber';
import { easing } from 'maath';   // npm i maath — damping without spring jitter

function Rig() {
  const scroll = useScroll();
  useFrame((state, dt) => {
    const p = scroll.offset;                       // 0..1
    easing.damp3(state.camera.position,
      [Math.sin(p * Math.PI) * 2.4, p * 2.6, 6 - p * 3.8], 0.3, dt);
    state.camera.lookAt(0, p * 0.4, 0);
  });
  return null;
}

<Canvas frameloop="always">
  <ScrollControls pages={3} damping={0.18}>
    <Rig />
    <Blob />
    <Scroll html>{/* real DOM content scrolls in sync */}</Scroll>
  </ScrollControls>
</Canvas>
```
`easing.damp3` is frame-rate independent — a raw `lerp(0.05)` runs at double speed on a
120 Hz display. Use damping for anything that follows a pointer or a scroll value.

## Postprocessing — one effect, not a stack

```tsx
import { EffectComposer, Bloom, Noise, Vignette } from '@react-three/postprocessing';

<EffectComposer multisampling={0} disableNormalPass>
  <Bloom intensity={0.6} luminanceThreshold={0.85} mipmapBlur />
  <Noise opacity={0.025} />
  <Vignette offset={0.25} darkness={0.55} />
</EffectComposer>
```
Every pass is a full-screen draw. Three passes is the ceiling on mobile; bloom alone
costs ~2 ms at 1080p. `multisampling={0}` matters — MSAA with a composer is wasted work.

## Perf guards

```tsx
import { PerformanceMonitor } from '@react-three/drei';
const [degraded, setDegraded] = useState(false);
<PerformanceMonitor onDecline={() => setDegraded(true)}>
  {!degraded && <EffectComposer>…</EffectComposer>}
</PerformanceMonitor>
```

Checklist before shipping an R3F scene:
- `dpr={[1, 2]}`, never uncapped
- `frameloop="demand"` unless continuously animating
- lazy `dynamic(..., { ssr: false })` with a designed poster fallback
- reduced-motion renders exactly one frame
- `<Preload all />` so materials compile before first reveal, not during it
- one heavy material max (transmission OR bloom, not both)
- test at 375px on a throttled CPU (DevTools 4× slowdown)
