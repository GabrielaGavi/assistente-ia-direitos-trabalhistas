import * as THREE from "/vendor/three.module.js";
import Lenis from "/vendor/lenis.mjs";

function startSmoothScroll(){
  if(matchMedia("(prefers-reduced-motion: reduce)").matches)return;
  const lenis=new Lenis({duration:1.05,smoothWheel:true,wheelMultiplier:.86});
  const raf=(time)=>{lenis.raf(time);requestAnimationFrame(raf)};
  requestAnimationFrame(raf);
}

function startHands(){
  const container=document.querySelector(".framer-gy7bn0-container");
  if(!container)return;
  container.querySelectorAll("video").forEach((video)=>video.remove());
  let host=container.querySelector("#interactive-hands-canvas");
  if(!host){host=document.createElement("div");host.id="interactive-hands-canvas";host.setAttribute("aria-hidden","true");container.appendChild(host)}
  if(host.dataset.started)return;
  host.dataset.started="1";
  host.dataset.state="initializing";
  const texture=new THREE.TextureLoader().load("/assets/optivio-hands-frame.png",()=>{host.dataset.state="ready"},undefined,()=>{host.dataset.state="texture-error"});
  texture.colorSpace=THREE.SRGBColorSpace;
  texture.minFilter=THREE.LinearFilter;texture.magFilter=THREE.LinearFilter;
  const renderer=new THREE.WebGLRenderer({antialias:false,alpha:false,powerPreference:"high-performance"});
  renderer.setClearColor(0x000000,1);renderer.setPixelRatio(Math.min(devicePixelRatio,1.6));host.appendChild(renderer.domElement);
  const scene=new THREE.Scene();
  const camera=new THREE.OrthographicCamera(-1,1,1,-1,0,1);
  const uniforms={
    map:{value:texture},time:{value:0},pointer:{value:new THREE.Vector2(.5,.5)},hover:{value:0},resolution:{value:new THREE.Vector2(1,1)},videoResolution:{value:new THREE.Vector2(1920,1080)}
  };
  const material=new THREE.ShaderMaterial({uniforms,depthTest:false,depthWrite:false,vertexShader:`
    varying vec2 vUv;
    void main(){vUv=uv;gl_Position=vec4(position,1.0);}
  `,fragmentShader:`
    precision highp float;
    uniform sampler2D map;uniform float time;uniform float hover;uniform vec2 pointer;uniform vec2 resolution;uniform vec2 videoResolution;varying vec2 vUv;
    vec2 coverUv(vec2 uv){float rs=resolution.x/resolution.y;float rv=videoResolution.x/videoResolution.y;if(rs>rv){float s=rv/rs;uv.y=(uv.y-.5)*s+.5;}else{float s=rs/rv;uv.x=(uv.x-.5)*s+.5;}return uv;}
    void main(){
      vec2 uv=vUv;
      float motionTime=time*(.78+hover*2.8);
      vec2 wave=vec2(
        sin(uv.y*19.0+motionTime)+sin(uv.y*41.0-motionTime*.58)*.38,
        cos(uv.x*16.0-motionTime*.86)+sin(uv.x*33.0+motionTime*.52)*.34
      );
      uv+=wave*(.0068+hover*.0115);
      float center=.535;
      float side=uv.x<center?-1.0:1.0;
      float idleDrift=sin(time*.7+side*1.2)*.009;
      float separation=.018+idleDrift+hover*.06;
      vec2 sampleUv=uv;sampleUv.x-=side*separation;
      sampleUv.y+=side*sin(motionTime*.73+side)*(.006+hover*.009);
      vec2 delta=uv-pointer;float distance=length(delta);float influence=smoothstep(.22,0.0,distance)*hover;
      float ripple=sin(distance*58.0-motionTime*4.0)*influence;
      sampleUv-=normalize(delta+vec2(.0001))*influence*(.058+ripple*.012);
      float gap=.013+hover*.021;
      if(abs(uv.x-center)<gap){gl_FragColor=vec4(0.,0.,0.,1.);return;}
      vec4 color=texture2D(map,coverUv(sampleUv));
      float edge=smoothstep(0.,.08,uv.x)*smoothstep(0.,.08,1.-uv.x)*smoothstep(0.,.06,uv.y)*smoothstep(0.,.06,1.-uv.y);
      color.rgb*=edge;
      gl_FragColor=vec4(color.rgb,1.);
    }
  `});
  const mesh=new THREE.Mesh(new THREE.PlaneGeometry(2,2),material);scene.add(mesh);
  let targetHover=0;
  const resize=()=>{const rect=host.getBoundingClientRect();renderer.setSize(rect.width,rect.height,false);uniforms.resolution.value.set(rect.width,rect.height);host.dataset.size=Math.round(rect.width)+"x"+Math.round(rect.height)};
  const move=(event)=>{const rect=host.getBoundingClientRect();uniforms.pointer.value.set((event.clientX-rect.left)/rect.width,1-(event.clientY-rect.top)/rect.height)};
  const interactionSurface=container.closest('[data-framer-name="Main-Container"]')||container.parentElement||host;
  interactionSurface.addEventListener("pointerenter",()=>{targetHover=1});interactionSurface.addEventListener("pointerleave",()=>{targetHover=0;uniforms.pointer.value.set(.5,.5)});interactionSurface.addEventListener("pointermove",move,{passive:true});
  new ResizeObserver(resize).observe(host);resize();
  const clock=new THREE.Clock();
  renderer.setAnimationLoop(()=>{uniforms.time.value=clock.getElapsedTime();uniforms.hover.value+=(targetHover-uniforms.hover.value)*(targetHover?.14:.055);renderer.render(scene,camera)});
}

const copy=new Map([
  ["Home","Início"],["About","Propósito"],["Services","Como funciona"],["Blog","Fontes"],["Pricing","Acesso"],["Contact us","Contato"],["Review capabilities","Abrir assistente"],["They trust us","Informação com lastro"],["4,9","CLT"],["Trusted by the best.","Construído sobre fontes oficiais."],["Proof of Impact","Princípios do produto"],["Results that speak for themselves","Humano na pergunta. Lei na fonte."],["Comparison","Transparência"],["Feature","Recursos"],["Explore dashboard","Abrir assistente"],["Try now","Experimentar"],["Buy Now","Abrir assistente"],["FAQ","Dúvidas frequentes"],["CTA","Comece agora"]
]);
const normalize=(value)=>value.replace(/\s+/g," ").trim();
function adaptCopy(){
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);const nodes=[];while(walker.nextNode())nodes.push(walker.currentNode);
  for(const node of nodes){const value=normalize(node.nodeValue||"");if(copy.has(value))node.nodeValue=(node.nodeValue||"").replace(value,copy.get(value));}
  document.querySelectorAll("h1").forEach((heading)=>{const value=normalize(heading.textContent||"");if(!value.includes("Turn traffic into")&&!value.includes("Transforme dúvidas em"))return;if(heading.dataset.cloneCopy)return;heading.dataset.cloneCopy="1";heading.innerHTML='Transforme dúvidas em <span class="direito-word">direitos</span><br>com clareza';});
  document.querySelectorAll(".framer-1pbewzh p").forEach((node)=>node.textContent="Orientação trabalhista clara, fundamentada e acompanhada de fontes que você pode conferir.");
  document.querySelectorAll(".framer-16w6mjk").forEach((wrapper)=>{if(wrapper.querySelector(".direito-prompt"))return;wrapper.innerHTML='<form class="direito-prompt" action="/chat" method="get"><input type="text" aria-label="Conte sua dúvida trabalhista" placeholder="Conte sua dúvida trabalhista..."><button type="submit" aria-label="Abrir assistente">↗</button></form>';});
  document.querySelectorAll("p").forEach((node)=>{const label=normalize(node.textContent||"");if(label.includes("Give it a try with our 14-day free trial"))node.textContent="Informação educativa. Cada resposta mostra as fontes utilizadas."});
  document.querySelectorAll('[data-framer-name="Logo Wrapper"]').forEach((wrapper)=>{if(wrapper.querySelector(".direito-logo"))return;wrapper.innerHTML='<a href="#" class="direito-logo"><span class="direito-logo-mark"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></span><span>Direito em claro</span></a>';});
  document.querySelectorAll("a,button").forEach((element)=>{const label=normalize(element.textContent||"").toLowerCase();if(!["abrir assistente","experimentar"].some((word)=>label.includes(word))||element.dataset.cloneAction)return;element.dataset.cloneAction="1";if(element.tagName==="A")element.setAttribute("href","/chat");});
  document.querySelectorAll("form").forEach((form)=>{form.setAttribute("action","/chat");form.setAttribute("method","get")});
  document.querySelectorAll("a,div").forEach((element)=>{const label=normalize(element.textContent||"");if(label==="Made in Framer"&&element.children.length<4)element.remove();if(label.includes("Only $48")){let target=element;while(target.parentElement&&getComputedStyle(target).position!=="fixed")target=target.parentElement;if(getComputedStyle(target).position==="fixed")target.remove();}});
  document.querySelectorAll("#__framer-badge-container").forEach((badge)=>badge.remove());
}

startSmoothScroll();startHands();adaptCopy();
[250,900,1800,3200].forEach((delay)=>setTimeout(()=>{startHands();adaptCopy()},delay));
let queued=false;new MutationObserver(()=>{if(queued)return;queued=true;requestAnimationFrame(()=>{queued=false;startHands();adaptCopy()})}).observe(document.documentElement,{childList:true,subtree:true});
