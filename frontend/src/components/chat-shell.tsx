"use client";

import Link from "next/link";
import { useEffect, useLayoutEffect, useRef, useState, type FormEvent } from "react";
import gsap from "gsap";
import Lenis from "lenis";
import { chatTopics } from "@/lib/chat-topics";
import styles from "./chat-shell.module.css";

type Message = { role: "user" | "assistant"; content: string };
const previewAnswer = "Recebi sua pergunta. Esta conversa ainda é uma demonstração: não estou consultando a base jurídica nem emitindo uma orientação sobre o seu caso. Quando a integração estiver disponível, esta área mostrará a explicação, os limites e as referências consultadas.";

export function ChatShell({ initialDraft = "", initialTopic }: { initialDraft?: string; initialTopic?: string }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState(initialDraft);
  const [topic, setTopic] = useState<string | undefined>(initialTopic);
  const [menuOpen, setMenuOpen] = useState(false);
  const root = useRef<HTMLElement>(null);
  const scroll = useRef<HTMLDivElement>(null);
  const content = useRef<HTMLDivElement>(null);
  const textarea = useRef<HTMLTextAreaElement>(null);
  const menu = useRef<HTMLElement>(null);
  const menuButton = useRef<HTMLButtonElement>(null);
  const closeButton = useRef<HTMLButtonElement>(null);
  const smooth = useRef<Lenis | null>(null);

  useEffect(() => {
    const wrapper = scroll.current, inner = content.current;
    if (!wrapper || !inner) return;
    const motion = matchMedia("(prefers-reduced-motion: reduce)");
    const lenis = new Lenis({ wrapper, content: inner, duration: 1.08, smoothWheel: !motion.matches, wheelMultiplier: .85, autoRaf: false, overscroll: false });
    smooth.current = lenis;
    const tick = (time: number) => lenis.raf(time * 1000);
    gsap.ticker.add(tick);
    const intro = gsap.context(() => {
      if (motion.matches) return;
      gsap.fromTo("[data-chat-intro]", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: .75, stagger: .07, ease: "power3.out" });
    }, root);
    return () => { intro.revert(); gsap.ticker.remove(tick); lenis.destroy(); smooth.current = null; };
  }, []);

  useLayoutEffect(() => {
    const input = textarea.current;
    if (!input) return;
    input.style.height = "auto";
    input.style.height = `${Math.min(input.scrollHeight, 144)}px`;
  }, [draft]);

  useEffect(() => {
    if (initialDraft) {
      textarea.current?.focus({ preventScroll: true });
      textarea.current?.setSelectionRange(initialDraft.length, initialDraft.length);
    }
  }, [initialDraft]);

  useEffect(() => {
    if (!messages.length || !content.current) return;
    const nodes = content.current.querySelectorAll("[data-message]");
    const animation = gsap.fromTo(Array.from(nodes).slice(-2), { opacity: 0, y: 10 }, { opacity: 1, y: 0, stagger: .10, duration: matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : .45, ease: "power2.out" });
    smooth.current?.resize();
    smooth.current?.scrollTo("bottom", { duration: .8 });
    return () => { animation.kill(); };
  }, [messages]);

  useEffect(() => {
    const viewport = window.visualViewport;
    const update = () => root.current?.style.setProperty("--chat-height", `${viewport?.height ?? window.innerHeight}px`);
    update(); viewport?.addEventListener("resize", update);
    return () => viewport?.removeEventListener("resize", update);
  }, []);

  useEffect(() => {
    if (!menuOpen) return;
    closeButton.current?.focus();
    const onKey = (event: KeyboardEvent) => {
      if (event.key === "Escape") { setMenuOpen(false); menuButton.current?.focus(); }
      if (event.key !== "Tab") return;
      const buttons = menu.current?.querySelectorAll<HTMLElement>("a[href],button");
      if (!buttons?.length) return;
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [menuOpen]);

  function choose(value: string, id?: string) {
    setDraft(value); setTopic(id); setMenuOpen(false);
    textarea.current?.focus({ preventScroll: true });
  }

  function send(event?: FormEvent) {
    event?.preventDefault();
    const question = draft.trim();
    if (!question) return;
    setMessages(current => [...current, { role: "user", content: question }, { role: "assistant", content: previewAnswer }]);
    setDraft("");
  }

  function reset() {
    setMessages([]); setDraft(""); setTopic(undefined); setMenuOpen(false);
    smooth.current?.scrollTo(0, { immediate: true });
    textarea.current?.focus({ preventScroll: true });
  }

  return <main ref={root} className={`${styles.app} ${menuOpen ? styles.menuOpen : ""}`}>
    <aside ref={menu} className={styles.sidebar} id="chat-navigation" aria-label="Navegação do assistente">
      <div className={styles.sidebarHeader}><Link href="/" className={styles.brand}><span aria-hidden="true">✣</span>Direito em Claro</Link><button ref={closeButton} className={styles.closeMenu} aria-label="Fechar menu" onClick={() => { setMenuOpen(false); menuButton.current?.focus(); }}>×</button></div>
      <button className={styles.newChat} onClick={reset}><span>Nova conversa</span><b aria-hidden="true">+</b></button>
      <nav className={styles.topics} aria-label="Temas trabalhistas"><p>ESCOLHA UM TEMA</p>{chatTopics.map((item, i) => <button key={item.id} aria-pressed={topic === item.id} onClick={() => choose(item.prompt, item.id)}><span>0{i + 1}</span>{item.label}<i aria-hidden="true">↗</i></button>)}</nav>
      <div className={styles.sidebarFooter}><span className={styles.status}><i /> DEMONSTRAÇÃO</span><p>Informação para começar.<br />Fontes para conferir.</p><Link href="/#arquitetura">Conheça o projeto <span>↗</span></Link></div>
    </aside>
    <button className={styles.backdrop} tabIndex={-1} aria-label="Fechar navegação" onClick={() => { setMenuOpen(false); menuButton.current?.focus(); }} />
    <section className={styles.stage} aria-label="Conversa">
      <header className={styles.topbar}><div><button ref={menuButton} className={styles.menuToggle} aria-label="Abrir navegação" aria-controls="chat-navigation" aria-expanded={menuOpen} onClick={() => setMenuOpen(true)}>☰</button><span>ASSISTENTE TRABALHISTA</span><span className={styles.topbarDivider}>/</span><small>Conversa {messages.length ? "em andamento" : "nova"}</small></div><Link href="/">Voltar ao site <span aria-hidden="true">↗</span></Link></header>
      <div ref={scroll} className={styles.scroll} data-chat-scroll>
        <div ref={content} className={styles.content}>
          {messages.length === 0 ? <div className={styles.welcome}>
            <p data-chat-intro className={styles.eyebrow}>[ SUA PERGUNTA É O PONTO DE PARTIDA ]</p>
            <h1 data-chat-intro>O que aconteceu<br />no seu <span>trabalho?</span></h1>
            <p data-chat-intro className={styles.lead}>Conte com suas palavras. Comece pelo que aconteceu e pelo que você precisa entender.</p>
          </div> : <div className={styles.messages} role="log" aria-live="polite" aria-relevant="additions">{messages.map((message, i) => <article data-message key={i} className={`${styles.message} ${message.role === "user" ? styles.userMessage : ""}`}><div className={styles.identity}><span aria-hidden="true">{message.role === "user" ? "↳" : "✣"}</span><b>{message.role === "user" ? "SUA PERGUNTA" : "DIREITO EM CLARO"}</b></div><p>{message.content}</p>{message.role === "assistant" && <div className={styles.sourceNotice}><span aria-hidden="true">↳</span>Resposta demonstrativa · nenhuma fonte consultada.</div>}</article>)}</div>}
        </div>
      </div>
      <div className={styles.composerDock}>
        <div className={styles.composerInner}>
          <form className={styles.composer} onSubmit={send}>
            <div className={styles.composerHeader}><label htmlFor="chat-question">{topic ? chatTopics.find(item => item.id === topic)?.label : "SUA PERGUNTA"}</label><span>Não inclua dados pessoais.</span></div>
            <div className={styles.inputRow}><textarea id="chat-question" ref={textarea} value={draft} onChange={event => setDraft(event.target.value)} placeholder="Escreva o que aconteceu no seu trabalho…" rows={2} data-lenis-prevent aria-describedby="chat-help" onKeyDown={event => { if (event.key === "Enter" && !event.shiftKey && !event.nativeEvent.isComposing) { event.preventDefault(); send(); } }} /><button type="submit" disabled={!draft.trim()} aria-label="Enviar pergunta">↑</button></div>
            <div className={styles.inputHint}><span>Enter para enviar</span><span>Shift + Enter para nova linha</span></div>
          </form>
          <p className={styles.disclaimer} id="chat-help">Conteúdo educativo. Não substitui atendimento jurídico profissional.</p>
        </div>
      </div>
    </section>
  </main>;
}
