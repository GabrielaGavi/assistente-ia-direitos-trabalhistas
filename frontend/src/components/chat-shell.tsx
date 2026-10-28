"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import gsap from "gsap";

type Message = { role: "user" | "assistant"; content: string };
const suggestions = ["Fui demitida sem justa causa. O que preciso verificar?", "Como funciona o adicional noturno?", "Quais documentos ajudam a comprovar horas extras?"];

export function ChatShell() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [draft, setDraft] = useState("");
  function send(value = draft) {
    const question = value.trim(); if (!question) return;
    setMessages((current) => [...current, { role: "user", content: question }, { role: "assistant", content: "Esta é uma prévia da interface. Quando a conexão com o backend estiver pronta, vou consultar fontes oficiais, destacar os limites da orientação e apresentar cada citação verificável aqui." }]);
    setDraft("");
    requestAnimationFrame(() => gsap.fromTo("[data-message]:last-child", { y: 12, opacity: 0 }, { y: 0, opacity: 1, duration: 0.35, ease: "power2.out" }));
  }
  function submit(event: FormEvent<HTMLFormElement>) { event.preventDefault(); send(); }
  return <main className="chatApp"><aside className="chatSidebar"><Link href="/" className="chatBrand"><span className="chatMark">✣</span>direito <em>em claro</em></Link><button className="newChat" onClick={() => { setMessages([]); setDraft(""); }}><span>＋</span> Nova conversa</button><div className="sidebarHistory"><p>HOJE</p><button onClick={() => setDraft(suggestions[0])}>Direitos após demissão</button><button onClick={() => setDraft(suggestions[1])}>Adicional noturno</button></div><div className="sidebarFoot"><span className="statusDot" /> fontes oficiais em breve</div></aside><section className="chatStage"><header className="chatTopbar"><button className="mobileMenu" aria-label="Abrir menu">☰</button><span>Assistente trabalhista <b>prévia</b></span><Link href="/">Sair ↗</Link></header><div className={`chatContent ${messages.length ? "hasMessages" : ""}`}>{messages.length === 0 ? <div className="chatWelcome"><p className="chatKicker">HUMANO NA PERGUNTA · LEI NA FONTE</p><h1>O que aconteceu no seu <em>trabalho?</em></h1><p>Conte com suas palavras. Vamos transformar sua dúvida em uma orientação clara, com referências para você conferir.</p><div className="suggestions">{suggestions.map((suggestion) => <button key={suggestion} onClick={() => send(suggestion)}>{suggestion}<span>↗</span></button>)}</div></div> : <div className="messages">{messages.map((message, index) => <article data-message key={`${message.role}-${index}`} className={`message ${message.role}`}><div className="messageIdentity">{message.role === "user" ? "VOCÊ" : "DIREITO EM CLARO"}</div><p>{message.content}</p>{message.role === "assistant" && <div className="citationPreview"><span>[ 01 ]</span><div><strong>Fontes e citações aparecerão aqui</strong><small>Integração pendente com o backend</small></div><b>↗</b></div>}</article>)}</div>}</div><form className="composer" onSubmit={submit}><textarea value={draft} onChange={(event) => setDraft(event.target.value)} placeholder="Conte sua dúvida trabalhista…" rows={1} onKeyDown={(event) => { if (event.key === "Enter" && !event.shiftKey) { event.preventDefault(); send(); } }} /><button type="submit" aria-label="Enviar pergunta">↑</button><p>Respostas educativas; não substitui orientação profissional.</p></form></section></main>;
}
