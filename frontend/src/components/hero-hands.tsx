"use client";

import { useMemo, useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";

gsap.registerPlugin(useGSAP);
type Dot = { x: number; y: number; mark: string; tone: string };

function makeDots(seed: number, accent: "human" | "system") {
  const marks = ["+", "·", "×", "○", "#", "⌁", "."];
  const tones = accent === "human" ? ["#f1a873", "#e8d4c3", "#e7f65a", "#9b6e52"] : ["#e7f65a", "#91d8c8", "#e5e5c6", "#b0c778"];
  const dots: Dot[] = []; let state = seed;
  const random = () => { state = (state * 16807) % 2147483647; return (state - 1) / 2147483646; };
  for (let row = 0; row < 31; row += 1) for (let column = 0; column < 38; column += 1) {
    if (random() > 0.68) continue;
    dots.push({ x: column * 16 + random() * 5, y: row * 15 + random() * 5, mark: marks[Math.floor(random() * marks.length)], tone: tones[Math.floor(random() * tones.length)] });
  }
  return dots;
}

export function HeroHands() {
  const root = useRef<SVGSVGElement>(null);
  const humanDots = useMemo(() => makeDots(41, "human"), []);
  const systemDots = useMemo(() => makeDots(77, "system"), []);
  useGSAP(() => {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    const timeline = gsap.timeline({ defaults: { ease: "power3.out" } });
    timeline.fromTo("[data-hand='human']", { xPercent: -13, opacity: 0 }, { xPercent: 0, opacity: 1, duration: 1.45 })
      .fromTo("[data-hand='system']", { xPercent: 15, opacity: 0 }, { xPercent: 0, opacity: 1, duration: 1.45 }, 0.1)
      .fromTo("[data-particle]", { opacity: 0, scale: 0.35 }, { opacity: 0.9, scale: 1, duration: 0.5, stagger: { each: 0.004, from: "random" } }, 0.3);
    gsap.to("[data-hand='human']", { y: -9, duration: 4.2, ease: "sine.inOut", yoyo: true, repeat: -1 });
    gsap.to("[data-hand='system']", { y: 10, duration: 4.8, ease: "sine.inOut", yoyo: true, repeat: -1 });
    gsap.to("[data-orbit]", { rotation: 360, transformOrigin: "50% 50%", duration: 34, ease: "none", repeat: -1 });
  }, { scope: root });
  return <svg ref={root} className="heroHands" viewBox="0 0 1200 720" aria-hidden="true" role="presentation"><defs>
    <clipPath id="human-hand"><path d="M-48 541C97 514 194 476 303 406c52-34 101-77 147-121l94-89c18-18 42-10 47 8 4 15-7 32-21 45l-78 73 161-100c24-15 48 18 25 35l-141 102 176-74c28-12 42 24 17 37l-151 85 147-39c28-7 38 30 11 39l-190 68c-62 22-124 42-189 55-100 20-208 44-350 111Z" /></clipPath>
    <clipPath id="system-hand"><path d="M1262 184c-147 20-242 55-344 111-58 32-112 72-164 112l-113 87c-21 16-47 4-47-16 0-16 14-29 30-41l92-68-179 85c-27 13-48-24-22-39l155-91-184 56c-29 9-37-29-10-39l159-64-151 23c-29 5-34-33-6-40l198-48c64-15 130-27 196-31 101-7 212-18 371-63Z" /></clipPath>
    <filter id="soft-glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="4" /></filter><radialGradient id="halo"><stop stopColor="#e7f65a" stopOpacity=".16" /><stop offset="1" stopColor="#e7f65a" stopOpacity="0" /></radialGradient>
  </defs><ellipse data-orbit cx="600" cy="350" rx="420" ry="165" fill="none" stroke="rgba(231,246,90,.16)" strokeDasharray="2 13" /><circle cx="600" cy="348" r="225" fill="url(#halo)" />
  <g data-hand="human" clipPath="url(#human-hand)"><rect x="0" y="120" width="620" height="510" fill="#f1a873" opacity=".055" />{humanDots.map((dot, index) => <text data-particle key={`h-${index}`} x={dot.x - 30} y={dot.y + 165} fill={dot.tone} fontSize="11" fontFamily="monospace">{dot.mark}</text>)}</g>
  <g data-hand="system" clipPath="url(#system-hand)"><rect x="560" y="120" width="640" height="510" fill="#e7f65a" opacity=".045" />{systemDots.map((dot, index) => <text data-particle key={`s-${index}`} x={dot.x + 595} y={dot.y + 112} fill={dot.tone} fontSize="11" fontFamily="monospace">{dot.mark}</text>)}</g>
  <circle cx="602" cy="346" r="5" fill="#e7f65a" filter="url(#soft-glow)" /><circle cx="602" cy="346" r="2" fill="#fff" /></svg>;
}
