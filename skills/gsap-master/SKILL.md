---
name: gsap-master
description: |
  Master suite for GreenSock Animation Platform (GSAP).
  Covers GSAP Core, Timelines, ScrollTrigger, React/Next.js integration, performance optimizations, and advanced plugin effects.
  Use when building high-performance web animations, scroll-driven interactive experiences, SVG animations, and motion designs.
---

# GSAP Master Animation Skill

Comprehensive animation standards, performance patterns, and integration guides for GreenSock Animation Platform (GSAP 3+).

## Core Capabilities & Modules

1. **GSAP Core**: Tweens, easing curves (`power2.out`, `elastic`, `back`, custom easing), `gsap.to()`, `gsap.from()`, `gsap.fromTo()`, and context cleanup.
2. **Timelines**: Complex sequencing, relative positioning (`<`, `+=0.5`, `>-0.2`), labels, nested timelines, control methods (`play`, `pause`, `reverse`, `restart`).
3. **ScrollTrigger**: Scroll-driven animations, pinning elements, scrub control, trigger start/end locations (`top 80%`, `center center`), toggleActions (`play pause resume reset`), snap configurations.
4. **React & Modern Framework Integration**: Proper `useGSAP()` hook usage, scoping refs, avoiding memory leaks, server-side rendering (SSR) safety (`gsap.registerPlugin()`).
5. **Plugins & Utilities**: Flip plugin, Observer, MotionPath, TextPlugin, SplitText, ScrambleText, `gsap.utils.mapRange()`, `gsap.utils.pipe()`, `gsap.utils.toArray()`.
6. **Performance Optimization**: `will-change`, transform-only animations (`x`, `y`, `scale`, `rotation`, `opacity`), avoiding layout thrashing, disabling unneeded renders when offscreen.

## Essential Code Patterns

### React / Next.js Setup (`useGSAP`)
```tsx
import { useRef } from 'react';
import gsap from 'gsap';
import { ScrollTrigger } from 'gsap/ScrollTrigger';
import { useGSAP } from '@gsap/react';

gsap.registerPlugin(ScrollTrigger, useGSAP);

export default function AnimatedSection() {
  const container = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    gsap.from('.fade-card', {
      y: 60,
      opacity: 0,
      duration: 0.8,
      stagger: 0.15,
      ease: 'power3.out',
      scrollTrigger: {
        trigger: container.current,
        start: 'top 75%',
        toggleActions: 'play none none reverse',
      },
    });
  }, { scope: container });

  return (
    <div ref={container} className="card-grid">
      <div className="fade-card">Item 1</div>
      <div className="fade-card">Item 2</div>
      <div className="fade-card">Item 3</div>
    </div>
  );
}
```

### Timeline Sequence
```js
const tl = gsap.timeline({ defaults: { ease: 'power2.out', duration: 0.6 } });

tl.to('.hero-title', { opacity: 1, y: 0 })
  .to('.hero-sub', { opacity: 1, y: 0 }, '-=0.3')
  .to('.hero-cta', { scale: 1, opacity: 1, ease: 'back.out(1.7)', '-=0.2' });
```
