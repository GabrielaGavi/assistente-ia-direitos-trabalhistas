"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useRef } from "react";
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { ParticleHands } from "./particle-hands";

gsap.registerPlugin(useGSAP);

const cards = [
  ["01", "Escuta primeiro", "Você conta o que aconteceu com suas palavras."],
  ["02", "Fontes oficiais", "A orientação é construída sobre documentos verificáveis."],
  ["03", "Resposta clara", "Contexto, limites e referências aparecem juntos."],
];

function BrandMark() {
  return <span className="brandGlyph" aria-hidden="true"><i /><i /><i /><i /><i /><i /><i /><i /></span>;
}

export function LandingPage() {
  const root = useRef<HTMLElement>(null);
  const router = useRouter();
  useGSAP(() => {
    gsap.from("[data-reveal]", { y: 36, opacity: 0, duration: 1, stagger: 0.12, ease: "power3.out" });
  }, { scope: root });

  return <main ref={root} className="landingPage">
    <section className="optivoHero" id="inicio">
      <header className="optivoNav" data-reveal>
        <Link href="#inicio" className="optivoBrand"><BrandMark /><span>Direito em claro</span></Link>
        <nav><a href="#inicio">Início</a><a href="#como-funciona">Como funciona</a><a href="#recursos">Recursos</a><a href="#fontes">Fontes</a></nav>
        <Link href="/chat" className="optivoButton">Abrir assistente <span>✣</span></Link>
      </header>
      <ParticleHands />
      <div className="heroVignette" />
      <div className="optivoHeroContent">
        <div className="heroProof" data-reveal><span>Informação com lastro</span><b>★★★★★</b><small>fontes oficiais</small></div>
        <h1 data-reveal>Transforme dúvidas em <em>clareza</em><br />com evidências.</h1>
        <p data-reveal>Orientação trabalhista acessível, fundamentada e construída para você conferir cada fonte.</p>
        <form data-reveal className="heroPrompt" onSubmit={(event) => { event.preventDefault(); router.push("/chat"); }}><input aria-label="Conte sua dúvida trabalhista" placeholder="Conte sua dúvida trabalhista..." /><button aria-label="Abrir assistente">↗</button></form>
        <small data-reveal className="heroDisclaimer">Informação educativa. Não substitui orientação jurídica profissional.</small>
      </div>
      <div className="heroBottom"><span /> <p>Construído para aproximar pessoas, tecnologia e direitos.</p> <span /></div>
    </section>

    <section className="impactSection" id="como-funciona">
      <div className="sectionLabel">COMO FUNCIONA</div><h2>Da sua história até a fonte,<br /><em>sem salto de fé.</em></h2>
      <div className="impactGrid">{cards.map(([number, title, text]) => <article key={number}><span>{number}</span><div className="cardSignal" /><h3>{title}</h3><p>{text}</p></article>)}</div>
    </section>

    <section className="featureBand" id="recursos"><div><div className="sectionLabel">O COMPROMISSO</div><h2>Tecnologia que amplia o acesso, sem esconder os limites.</h2><p>O assistente organiza contexto, procura evidências e mostra o caminho até o documento original.</p><Link href="/chat" className="lightButton">Conhecer a interface ↗</Link></div><div className="featureList"><article><span>01</span><h3>Citações verificáveis</h3><p>Cada afirmação importante aponta para sua origem.</p></article><article><span>02</span><h3>Linguagem acessível</h3><p>Direito trabalhista explicado sem juridiquês desnecessário.</p></article><article><span>03</span><h3>Limites explícitos</h3><p>A tecnologia informa quando é hora de procurar ajuda humana.</p></article></div></section>

    <section className="landingCta" id="fontes"><p>PRONTO PARA COMEÇAR?</p><h2>Sua dúvida merece uma resposta que você possa <em>conferir.</em></h2><Link href="/chat" className="optivoButton">Conversar com o assistente <span>↗</span></Link></section>
    <footer className="landingFooter"><div className="optivoBrand"><BrandMark /><span>Direito em claro</span></div><p>Informação trabalhista com fontes oficiais.</p><p>Brasil · 2026</p></footer>
  </main>;
}
