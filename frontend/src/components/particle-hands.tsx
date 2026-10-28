"use client";

import { useEffect, useRef } from "react";

type Particle = {
  x: number;
  y: number;
  side: -1 | 1;
  color: string;
  size: number;
  phase: number;
};

const W = 1400;
const H = 760;

function handPath() {
  const path = new Path2D();
  path.moveTo(-80, 690);
  path.bezierCurveTo(105, 655, 230, 590, 350, 520);
  path.bezierCurveTo(410, 486, 454, 445, 500, 404);
  path.lineTo(583, 337);
  path.bezierCurveTo(600, 324, 621, 327, 625, 343);
  path.bezierCurveTo(629, 357, 613, 369, 598, 378);
  path.lineTo(535, 419);
  path.lineTo(620, 378);
  path.bezierCurveTo(642, 367, 662, 373, 664, 388);
  path.bezierCurveTo(666, 402, 649, 412, 634, 420);
  path.lineTo(557, 459);
  path.lineTo(629, 435);
  path.bezierCurveTo(651, 428, 668, 437, 666, 452);
  path.bezierCurveTo(664, 466, 648, 472, 630, 477);
  path.lineTo(544, 502);
  path.lineTo(604, 491);
  path.bezierCurveTo(626, 488, 639, 500, 634, 514);
  path.bezierCurveTo(629, 527, 611, 531, 594, 533);
  path.lineTo(501, 547);
  path.bezierCurveTo(442, 557, 401, 577, 350, 611);
  path.bezierCurveTo(245, 681, 139, 726, -40, 776);
  path.closePath();
  return path;
}

function buildParticles() {
  const mask = document.createElement("canvas");
  mask.width = W;
  mask.height = H;
  const context = mask.getContext("2d", { willReadFrequently: true });
  if (!context) return [];
  const base = handPath();
  context.fillStyle = "#fff";
  context.fill(base);
  context.save();
  context.translate(W, H);
  context.scale(-1, -1);
  context.fill(base);
  context.restore();
  const pixels = context.getImageData(0, 0, W, H).data;
  const particles: Particle[] = [];
  const warm = ["#f1a873", "#d98452", "#f2ded0", "#c66b3d", "#ffbf80"];
  const cool = ["#f8ff62", "#dbe85b", "#f2f3d7", "#94b967", "#c9d79a"];
  for (let y = 0; y < H; y += 7) {
    for (let x = 0; x < W; x += 7) {
      if (pixels[(y * W + x) * 4 + 3] < 100 || Math.random() > 0.7) continue;
      const side: -1 | 1 = x < W / 2 ? -1 : 1;
      const palette = side === -1 ? warm : cool;
      particles.push({ x, y, side, color: palette[Math.floor(Math.random() * palette.length)], size: 0.7 + Math.random() * 1.35, phase: Math.random() * Math.PI * 2 });
    }
  }
  return particles;
}

export function ParticleHands() {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const context = canvas.getContext("2d");
    if (!context) return;
    const particles = buildParticles();
    let frame = 0;
    let width = 1;
    let height = 1;
    let pointerX = 0.5;
    let pointerY = 0.5;
    let interaction = 0;
    let interactionTarget = 0;

    const resize = () => {
      const bounds = canvas.getBoundingClientRect();
      const ratio = Math.min(window.devicePixelRatio || 1, 1.7);
      width = bounds.width;
      height = bounds.height;
      canvas.width = Math.max(1, Math.round(width * ratio));
      canvas.height = Math.max(1, Math.round(height * ratio));
      context.setTransform(ratio, 0, 0, ratio, 0, 0);
    };

    const draw = (time: number) => {
      context.clearRect(0, 0, width, height);
      interaction += (interactionTarget - interaction) * (interactionTarget ? 0.075 : 0.035);
      const scale = Math.max(width / W, height / H);
      const offsetX = (width - W * scale) / 2;
      const offsetY = (height - H * scale) / 2;
      const px = pointerX * width;
      const py = pointerY * height;
      const speed = 0.00034 + interaction * 0.00072;
      context.globalCompositeOperation = "lighter";

      for (const particle of particles) {
        const baseX = offsetX + particle.x * scale;
        const baseY = offsetY + particle.y * scale;
        const waterX = Math.sin(time * speed + particle.y * 0.018 + particle.phase * 0.15) * (2.2 + interaction * 5.5);
        const waterY = Math.sin(time * speed * 1.23 + particle.x * 0.016 + particle.phase * 0.12) * (3 + interaction * 7);
        const retreat = particle.side * interaction * 54;
        let x = baseX + waterX + retreat;
        let y = baseY + waterY;
        const dx = x - px;
        const dy = y - py;
        const distance = Math.hypot(dx, dy);
        if (interaction > 0.01 && distance < 125) {
          const force = (1 - distance / 125) * 31 * interaction;
          x += (dx / Math.max(distance, 1)) * force;
          y += (dy / Math.max(distance, 1)) * force;
        }
        const alpha = 0.54 + Math.sin(time * 0.001 + particle.phase) * 0.2;
        context.globalAlpha = alpha;
        context.fillStyle = particle.color;
        const size = particle.size + interaction * 0.35;
        if (particle.phase > 4.8) context.fillText(particle.side === -1 ? "+" : "·", x, y);
        else context.fillRect(x, y, size, size);
      }
      context.globalAlpha = 1;
      context.globalCompositeOperation = "source-over";
      frame = requestAnimationFrame(draw);
    };

    const move = (event: PointerEvent) => {
      const bounds = canvas.getBoundingClientRect();
      pointerX = (event.clientX - bounds.left) / bounds.width;
      pointerY = (event.clientY - bounds.top) / bounds.height;
    };
    const enter = () => { interactionTarget = 1; };
    const leave = () => { interactionTarget = 0; pointerX = 0.5; pointerY = 0.5; };
    resize();
    window.addEventListener("resize", resize, { passive: true });
    canvas.addEventListener("pointermove", move);
    canvas.addEventListener("pointerenter", enter);
    canvas.addEventListener("pointerleave", leave);
    frame = requestAnimationFrame(draw);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
      canvas.removeEventListener("pointermove", move);
      canvas.removeEventListener("pointerenter", enter);
      canvas.removeEventListener("pointerleave", leave);
    };
  }, []);

  return <canvas ref={canvasRef} className="particleHands" aria-hidden="true" />;
}
