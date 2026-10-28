"use client";

import { useEffect } from "react";

export function LandingBehavior() {
  useEffect(() => {
    const root = document.querySelector(".optivioLanding");
    if (!root) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const animations: Animation[] = [];
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(({ target, isIntersecting }) => {
        if (!isIntersecting) return;
        if (!reduced) animations.push(target.animate([
          { opacity: 0, transform: "translateY(35px)" },
          { opacity: 1, transform: "translateY(0)" },
        ], { duration: 800, easing: "cubic-bezier(.22,1,.36,1)" }));
        observer.unobserve(target);
      });
    }, { threshold: 0.08 });
    root.querySelectorAll("[data-landing-appear]").forEach(element => observer.observe(element));
    const videos = root.querySelectorAll("video");
    const videoObserver = new IntersectionObserver(entries => {
      entries.forEach(({ target, isIntersecting }) => {
        const video = target as HTMLVideoElement;
        if (isIntersecting && !reduced) void video.play().catch(() => {});
        else video.pause();
      });
    });
    videos.forEach(video => videoObserver.observe(video));
    const marquees = new Map<Element, Animation>();
    const marqueeObserver = new ResizeObserver(entries => {
      if (reduced) return;
      entries.forEach(({ target }) => {
        marquees.get(target)?.cancel();
        const items = [...target.children].slice(0, target.children.length / 2);
        const distance = items.reduce((sum, item) => sum + item.getBoundingClientRect().width + 8, 0);
        if (distance > 8) marquees.set(target, target.animate([
          { transform: "translateX(-8px)" }, { transform: `translateX(-${distance + 8}px)` },
        ], { duration: 25000, iterations: Infinity, easing: "linear" }));
      });
    });
    root.querySelectorAll('[data-framer-name="Clients-marquee"] ul').forEach(list => marqueeObserver.observe(list));
    const sections = [...root.querySelectorAll<HTMLElement>('[data-framer-name$="section"]')];
    let frame = 0;
    const updateNavigation = () => {
      frame = 0;
      const current = sections.find(section => {
        const rect = section.getBoundingClientRect();
        return rect.top <= 100 && rect.bottom > 100;
      });
      const dark = ["inicio", "crescimento", "comecar"].includes(current?.id ?? "inicio");
      (root as HTMLElement).dataset.navTheme = window.scrollY < 120 ? "initial" : dark ? "dark" : "light";
    };
    const scroll = () => { if (!frame) frame = requestAnimationFrame(updateNavigation); };
    window.addEventListener("scroll", scroll, { passive: true });
    updateNavigation();
    return () => {
      observer.disconnect(); videoObserver.disconnect();
      marqueeObserver.disconnect(); marquees.forEach(animation => animation.cancel());
      window.removeEventListener("scroll", scroll); cancelAnimationFrame(frame);
      animations.forEach(animation => animation.cancel());
      videos.forEach(video => video.pause());
    };
  }, []);
  return null;
}
