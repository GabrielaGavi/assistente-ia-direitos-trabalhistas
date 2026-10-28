"use client";

import { useEffect, useRef } from "react";

// Same texture, exposure and rigid motion as the approved canvas.
export function LandingHands() {
  const host = useRef<HTMLDivElement>(null);

  useEffect(() => {
    let disposed = false;
    let release: (() => void) | undefined;
    if (host.current) host.current.dataset.state = "loading";
    void import("three").then((THREE) => {
      if (disposed || !host.current) return;
      const element = host.current;
      const renderer = new THREE.WebGLRenderer({ antialias: false, alpha: false, powerPreference: "high-performance" });
      renderer.setClearColor(0x000000, 1);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.6));
      element.appendChild(renderer.domElement);
      const texture = new THREE.TextureLoader().load("/assets/optivio-hands-frame.png", () => {
        if (!disposed) element.dataset.state = "ready";
      });
      texture.colorSpace = THREE.SRGBColorSpace;
      texture.minFilter = THREE.LinearFilter;
      texture.magFilter = THREE.LinearFilter;
      const uniforms = {
        map: { value: texture }, time: { value: 0 },
        resolution: { value: new THREE.Vector2(1, 1) },
        videoResolution: { value: new THREE.Vector2(1920, 1080) },
      };
      const material = new THREE.ShaderMaterial({
        uniforms, depthTest: false, depthWrite: false,
        vertexShader: `varying vec2 vUv; void main(){vUv=uv;gl_Position=vec4(position,1.0);}`,
        fragmentShader: `
          precision highp float;
          uniform sampler2D map; uniform float time; uniform vec2 resolution;
          uniform vec2 videoResolution; varying vec2 vUv;
          vec2 coverUv(vec2 uv){float rs=resolution.x/resolution.y;float rv=videoResolution.x/videoResolution.y;if(rs>rv){float s=rv/rs;uv.y=(uv.y-.5)*s+.5;}else{float s=rs/rv;uv.x=(uv.x-.5)*s+.5;}return uv;}
          void main(){
            vec2 uv=coverUv(vUv);
            float side=uv.x<.5?-1.0:1.0;
            float separation=.028+sin(time*.8+side*.8)*.018;
            vec2 sampleUv=uv-vec2(side*separation,sin(time*.65+side*1.1)*.022);
            if(sampleUv.x<0.0||sampleUv.x>1.0||sampleUv.y<0.0||sampleUv.y>1.0){gl_FragColor=vec4(0.,0.,0.,1.);return;}
            vec4 color=texture2D(map,sampleUv);
            float edge=smoothstep(0.,.08,vUv.x)*smoothstep(0.,.08,1.-vUv.x)*smoothstep(0.,.06,vUv.y)*smoothstep(0.,.06,1.-vUv.y);
            float exposure=side>0.0?2.6:1.65;
            color.rgb=clamp(color.rgb*exposure,0.0,1.0)*edge;
            gl_FragColor=vec4(color.rgb,1.);
          }`,
      });
      const geometry = new THREE.PlaneGeometry(2, 2);
      const scene = new THREE.Scene();
      scene.add(new THREE.Mesh(geometry, material));
      const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0, 1);
      const resize = () => {
        const { width, height } = element.getBoundingClientRect();
        renderer.setSize(width, height, false);
        uniforms.resolution.value.set(width, height);
      };
      const observer = new ResizeObserver(resize);
      observer.observe(element);
      resize();
      const start = performance.now();
      const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
      renderer.setAnimationLoop(() => {
        uniforms.time.value = reducedMotion.matches ? 0 : (performance.now() - start) / 1000;
        renderer.render(scene, camera);
      });
      release = () => {
        observer.disconnect(); renderer.setAnimationLoop(null);
        geometry.dispose(); material.dispose(); texture.dispose(); renderer.dispose();
        renderer.domElement.remove();
      };
    }).catch(() => {
      if (host.current && !disposed) host.current.dataset.state = "error";
    });
    return () => { disposed = true; release?.(); };
  }, []);

  return <div ref={host} id="interactive-hands-canvas" aria-hidden="true" />;
}
