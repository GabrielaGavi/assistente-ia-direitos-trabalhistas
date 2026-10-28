"use client";

import { useEffect } from "react";
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

export function ImpactMotion() {
  useEffect(() => {
    const grid = document.getElementById("impact-grid");
    if (!grid) return;

    const media = gsap.matchMedia();
    let active = true;

    media.add("(min-width: 810px) and (prefers-reduced-motion: no-preference)", () => {
      // The reference opens the stack while the grid enters the viewport,
      // reaching its full layout when the bottom of the grid becomes visible.
      const timeline = gsap.timeline({
        defaults: { ease: "none" },
        scrollTrigger: {
          trigger: grid,
          start: "top bottom",
          end: "bottom bottom",
          scrub: true,
          invalidateOnRefresh: true,
        },
      });

      for (const [name, side, row] of [
        ["impact-card-1", 1, 1], ["impact-card-2", 1, -1],
        ["impact-card-4", -1, 1], ["impact-card-5", -1, -1],
      ] as const) {
        const card = grid.querySelector<HTMLElement>(`[data-framer-name="${name}"]`);
        if (!card) continue;
        timeline.fromTo(card, {
          x: () => side * Math.round(card.offsetWidth + 8),
          y: () => row * (card.offsetHeight + 8) / 2,
          scale: 0.8,
        }, { x: 0, y: 0, scale: 1 }, 0);
      }

      const center = [...grid.querySelectorAll<HTMLElement>(".framer-12atznz")]
        .find(element => element.offsetWidth > 0);
      if (center) timeline.fromTo(center, { scale: 0.8 }, { scale: 1 }, 0);
    });

    media.add("(prefers-reduced-motion: no-preference)", () => {
      for (const card of grid.querySelectorAll<HTMLElement>('[data-framer-name^="impact-card-"]')) {
        const icon = card.querySelector("svg");
        if (!icon) continue;
        gsap.fromTo(icon, { opacity: 0, scale: 0.7 }, {
          opacity: 1, scale: 1, duration: 0.65, ease: "back.out(1.4)",
          scrollTrigger: { trigger: card, start: "top 95%", once: true },
        });
      }
    });

    // Font loading can move the heading above the grid after the first render.
    void document.fonts.ready.then(() => { if (active) ScrollTrigger.refresh(); });

    return () => { active = false; media.revert(); };
  }, []);

  return null;
}
