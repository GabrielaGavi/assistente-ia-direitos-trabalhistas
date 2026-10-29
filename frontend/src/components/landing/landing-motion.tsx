"use client";

import { useEffect } from "react";

export function LandingMotion() {
  useEffect(() => {
    if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const animations: Animation[] = [];
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        animations.push(entry.target.animate([{ opacity: .1, transform: "translateY(22px)" }, { opacity: 1, transform: "translateY(0)" }], { duration: 800, easing: "cubic-bezier(.22,1,.36,1)" }));
        observer.unobserve(entry.target);
      });
    }, { threshold: .18 });
    document.querySelectorAll("[data-reveal]").forEach(el => observer.observe(el));
    return () => { observer.disconnect(); animations.forEach(animation => animation.cancel()); };
  }, []);
  return null;
}
