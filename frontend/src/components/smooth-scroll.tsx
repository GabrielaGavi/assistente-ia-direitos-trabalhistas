"use client";

import { useEffect } from "react";
import Lenis from "lenis";
import gsap from "gsap";
import { usePathname } from "next/navigation";
import "lenis/dist/lenis.css";

export function SmoothScroll() {
  const pathname = usePathname();
  useEffect(() => {
    if (pathname.startsWith("/chat")) return;
    const lenis = new Lenis({
      duration: 1.2,
      smoothWheel: !window.matchMedia("(prefers-reduced-motion: reduce)").matches,
      wheelMultiplier: 0.85,
      anchors: { offset: -88, duration: 1.1 },
      autoRaf: false,
    });
    const update = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(update);
    return () => { gsap.ticker.remove(update); lenis.destroy(); };
  }, [pathname]);
  return null;
}
