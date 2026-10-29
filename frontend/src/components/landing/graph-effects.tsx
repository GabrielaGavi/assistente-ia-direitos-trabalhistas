"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type CanvasDraw = (ctx: CanvasRenderingContext2D, width: number, height: number, time: number) => void;

function useVisibleCanvas(draw: CanvasDraw) {
  const ref = useRef<HTMLCanvasElement>(null);
  useEffect(() => {
    const canvas = ref.current;
    const ctx = canvas?.getContext("2d");
    if (!canvas || !ctx) return;
    let frame = 0, width = 1, height = 1, previous = 0, elapsed = 0;
    let visible = false;
    const motion = matchMedia("(prefers-reduced-motion: reduce)");
    const paint = (now: number) => {
      frame = 0;
      if (!visible || document.hidden) return;
      if (now - previous > 14 || motion.matches) {
        elapsed += Math.min(now - previous, 50) / 1000;
        previous = now;
        ctx.clearRect(0, 0, width, height);
        draw(ctx, width, height, motion.matches ? 0 : elapsed);
      }
      if (!motion.matches) frame = requestAnimationFrame(paint);
    };
    const start = () => {
      cancelAnimationFrame(frame);
      if (visible && !document.hidden) frame = requestAnimationFrame(paint);
    };
    const resize = new ResizeObserver(() => {
      const rect = canvas.getBoundingClientRect();
      width = rect.width; height = rect.height;
      const dpr = Math.min(devicePixelRatio, 2);
      canvas.width = Math.round(width * dpr); canvas.height = Math.round(height * dpr);
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      start();
    });
    const visibility = new IntersectionObserver(([entry]) => { visible = entry.isIntersecting; start(); });
    resize.observe(canvas); visibility.observe(canvas);
    document.addEventListener("visibilitychange", start); motion.addEventListener("change", start);
    return () => {
      cancelAnimationFrame(frame); resize.disconnect(); visibility.disconnect();
      document.removeEventListener("visibilitychange", start); motion.removeEventListener("change", start);
    };
  }, [draw]);
  return ref;
}

type FaceReference = { pixels: Uint8ClampedArray; width: number; height: number; aspect: number };

// These are the same separate squares as the hero field. The reference only
// supplies a silhouette and luminance; no image/texture is painted on screen.
export function drawPixelField(ctx: CanvasRenderingContext2D, width: number, height: number, time: number, face: FaceReference | null) {
  const bodyExtension = Math.min(112, Math.max(64, height * .13));
  const faceWidth = Math.min(width * .90, (height - bodyExtension - 24) * (face?.aspect ?? .90));
  const faceHeight = faceWidth / (face?.aspect ?? .90);
  const faceX = (width - faceWidth) / 2;
  const faceY = height - faceHeight - bodyExtension;
  const formation = face ? (time === 0 ? 1 : Math.min(1, Math.max(0, (time - .15) / 2))) : 0;
  const ease = formation * formation * (3 - 2 * formation);
  const animated = time !== 0;
  const floatX = animated ? Math.sin(time * .38) * 5 : 0;
  const floatY = animated ? Math.sin(time * .46) * 8 : 0;
  const breatheScale = animated ? 1 + Math.sin(time * .57) * .012 : 1;
  const centerX = faceX + faceWidth / 2, centerY = faceY + faceHeight / 2;

  for (let y = 0; y < height; y += 9) {
    const edge = width * (.30 + .13 * Math.sin(y / 180 + time * .19) + .06 * Math.sin(y / 70 - time * .24));
    for (let x = 0; x < width; x += 9) {
      const density = Math.max(0, Math.min(1, (x - edge) / (width * .54)));
      const wave = (Math.sin(x * .11 + y * .08 + time * .2) + 1) / 2;
      const noise = ((x * 13 + y * 79) % 101) / 101;
      const fieldAlpha = noise <= density ? .045 + density * .12 + wave * .045 : 0;
      let faceAlpha = 0;
      let faceSize = 0;
      let faceWeight = 0;
      let depth = 0;
      if (face) {
        let u = (x - faceX) / faceWidth;
        const v = (y - faceY) / faceHeight;
        // Continue the neck using the last stone rows of the reference. The
        // lower end widens slightly and stays anchored to the section boundary.
        const extension = Math.max(0, (y - faceY - faceHeight) / bodyExtension);
        if (v >= 1) u = .5 + (u - .5) / (1 + extension * .10);
        if (u >= 0 && u < 1 && v >= 0) {
          const referenceY = v < 1 ? v : .97 + Math.sin(extension * 4.5) * .015;
          const offset = (Math.min(face.height - 1, Math.floor(referenceY * face.height)) * face.width + Math.floor(u * face.width)) * 4;
          const r = face.pixels[offset] / 255, g = face.pixels[offset + 1] / 255, b = face.pixels[offset + 2] / 255;
          // White in the reference is empty space, not a white background.
          const silhouette = 1 - Math.min(1, Math.max(0, (Math.min(r, g, b) - .88) / .09));
          const luminance = r * .299 + g * .587 + b * .114;
          const light = Math.pow(Math.max(0, Math.min(1, (luminance - .24) / .61)), 1.7);
          const breathe = animated ? .94 + .06 * Math.sin(time * .6 + y * .012) : 1;
          faceAlpha = silhouette * (.12 + light * .88) * breathe;
          faceSize = silhouette * (3.2 + light * 3.2);
          faceWeight = silhouette;
          depth = light;
        }
      }
      const alpha = fieldAlpha * (1 - ease * .7) + faceAlpha * ease;
      if (alpha < .015) continue;
      const shimmer = animated ? 1 + Math.sin(time * .72 + y * .018) * .05 : 1;
      const size = ((2 + density * 3.3) * (1 - ease) + Math.max(2, faceSize) * ease) * shimmer;
      // The faint field continues around the brighter face: a single grid.
      const drift = animated ? Math.sin(time * .35 + y * .018) * 1.8 : 0;
      // Coherent low-frequency waves keep the face recognizable. Pixel positions
      // continue moving after formation, rather than stopping when ease reaches 1.
      const anchor = Math.min(1, Math.max(0, (height - y) / 92));
      const weight = faceWeight * ease * anchor;
      const waveX = animated ? Math.sin(y / height * 7 - time * .65) * 3.2 : 0;
      const waveY = animated ? Math.sin(x / width * 5 + time * .53) * 2 : 0;
      const relief = animated ? Math.sin(time * .38) * depth * 5 : 0;
      const px = x + drift * (1 - weight) + weight * (floatX + waveX + relief + (x - centerX) * (breatheScale - 1));
      const py = y + weight * (floatY + waveY + (y - centerY) * (breatheScale - 1));
      ctx.fillStyle = `rgba(246,244,237,${Math.min(1, alpha)})`;
      const pixelHeight = faceWeight > .5 && y > height - 9 ? Math.max(size, height - y + 1) : size;
      ctx.fillRect(px, py, size, pixelHeight);
    }
  }
}

export function PixelField({ className }: { className: string }) {
  const [face, setFace] = useState<FaceReference | null>(null);
  useEffect(() => {
    let active = true;
    const image = new Image();
    image.onload = () => {
      if (!active) return;
      const guide = document.createElement("canvas");
      guide.width = 180; guide.height = 200;
      const ctx = guide.getContext("2d", { willReadFrequently: true });
      if (!ctx) return;
      const cropWidth = image.width * .345, cropHeight = image.height * .685;
      ctx.drawImage(image, image.width * .651, image.height * .315, cropWidth, cropHeight, 0, 0, guide.width, guide.height);
      setFace({ pixels: ctx.getImageData(0, 0, guide.width, guide.height).data, width: guide.width, height: guide.height, aspect: cropWidth / cropHeight });
    };
    image.src = "/assets/statue-head.webp";
    return () => { active = false; image.onload = null; };
  }, []);
  const draw = useCallback<CanvasDraw>((ctx, width, height, time) => drawPixelField(ctx, width, height, time, face), [face]);
  return <canvas ref={useVisibleCanvas(draw)} className={className} aria-hidden="true" />;
}

const points = Array.from({ length: 460 }, (_, i) => {
  const y = 1 - (i / 459) * 2;
  const radius = Math.sqrt(1 - y * y);
  const angle = i * Math.PI * (3 - Math.sqrt(5));
  return { x: Math.cos(angle) * radius, y, z: Math.sin(angle) * radius };
});
const links = points.flatMap((p, i) => [17, 43, 97].map(offset => [i, (i + offset) % points.length] as const));

export function KnowledgeSphere({ className }: { className: string }) {
  const pointer = useRef({ x: -1000, y: -1000, active: false });
  const draw = useCallback<CanvasDraw>((ctx, width, height, time) => {
    const radius = Math.min(width * .42, height * .43);
    const cx = width / 2, cy = height / 2, angle = time * .075;
    const projected = points.map(p => {
      const x = p.x * Math.cos(angle) - p.z * Math.sin(angle);
      const z = p.x * Math.sin(angle) + p.z * Math.cos(angle);
      return { x: cx + x * radius, y: cy + (p.y * .96 + z * .24) * radius, z };
    });
    let selected = -1, distance = 90;
    if (pointer.current.active) projected.forEach((p, i) => {
      const d = Math.hypot(p.x - pointer.current.x, p.y - pointer.current.y);
      if (d < distance) { distance = d; selected = i; }
    });
    ctx.lineWidth = .5;
    for (const [a, b] of links) {
      const p = projected[a], q = projected[b];
      ctx.strokeStyle = `rgba(246,244,237,${selected >= 0 ? .055 : .09 + (p.z + q.z + 2) * .028})`;
      ctx.beginPath(); ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y); ctx.stroke();
    }
    projected.forEach((p, i) => {
      const size = i % 19 === 0 ? 5 : 1.3 + (p.z + 1) * .6;
      ctx.fillStyle = `rgba(246,244,237,${selected >= 0 ? .20 : .3 + (p.z + 1) * .32})`;
      ctx.fillRect(p.x - size / 2, p.y - size / 2, size, size);
    });
    if (selected >= 0) {
      const node = projected[selected];
      ctx.strokeStyle = "#fffe54"; ctx.lineWidth = 1;
      [17, 43, 97, 171].forEach(offset => {
        const end = projected[(selected + offset) % points.length];
        ctx.beginPath(); ctx.moveTo(node.x, node.y); ctx.lineTo(end.x, end.y); ctx.stroke();
        ctx.fillStyle = "#f6f4ed"; ctx.fillRect(end.x - 3, end.y - 3, 6, 6);
      });
      ctx.beginPath(); ctx.arc(node.x, node.y, 9, 0, Math.PI * 2); ctx.stroke();
      const labelX = Math.min(node.x + 16, width - 155);
      ctx.fillStyle = "#10110f"; ctx.fillRect(labelX - 5, node.y - 12, 150, 25);
      ctx.fillStyle = "#fffe54"; ctx.font = "12px monospace";
      ctx.fillText(["CLT · DOCUMENTO", "FGTS · TEMA", "FONTE · OFICIAL", "TRECHO · EVIDÊNCIA"][selected % 4], labelX, node.y + 4);
    }
  }, []);
  const canvas = useVisibleCanvas(draw);
  return <canvas ref={canvas} className={className} aria-hidden="true" onPointerMove={event => {
    const rect = event.currentTarget.getBoundingClientRect();
    pointer.current = { x: event.clientX - rect.left, y: event.clientY - rect.top, active: true };
  }} onPointerLeave={() => { pointer.current.active = false; }} />;
}
