"use client";

import { useEffect, useId, useRef, useState } from "react";
import gsap from "gsap";
import styles from "./direito-site.module.css";

const questions = [
  ["O assistente substitui atendimento jurídico?", "O conteúdo é informativo e educativo. Situações que exigem análise individual precisam de apoio de advogado, sindicato ou serviço público especializado."],
  ["Como conferir uma orientação?", "Leia os limites informados e consulte as fontes apresentadas. A procedência do documento é parte da explicação."],
  ["Quais informações devo compartilhar?", "Conte o que aconteceu sem incluir senhas, documentos pessoais ou dados sensíveis de outras pessoas."],
  ["O que já posso experimentar?", "A interface de conversa está em demonstração. A integração com a base de documentos e a geração de respostas está em desenvolvimento."],
];

function FaqRow({ question, answer }: { question: string; answer: string }) {
  const [open, setOpen] = useState(false);
  const id = useId();
  const panel = useRef<HTMLDivElement>(null);
  const text = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const node = panel.current;
    const inner = text.current;
    if (!node || !inner) return;
    const animation = gsap.to(node, {
      height: open ? inner.offsetHeight : 0,
      opacity: open ? 1 : 0,
      duration: matchMedia("(prefers-reduced-motion: reduce)").matches ? 0 : .48,
      ease: "power3.inOut",
      overwrite: true,
      onComplete: () => { if (open) node.style.height = "auto"; },
    });
    return () => { animation.kill(); };
  }, [open]);
  return <article className={styles.faqRow}>
    <h3><button id={`${id}-button`} aria-expanded={open} aria-controls={`${id}-panel`} onClick={() => setOpen(value => !value)}>{question}<span aria-hidden="true" className={open ? styles.faqOpen : ""}>+</span></button></h3>
    <div ref={panel} id={`${id}-panel`} className={styles.faqPanel} role="region" aria-labelledby={`${id}-button`} aria-hidden={!open}><div ref={text}><p>{answer}</p></div></div>
  </article>;
}

export function AnimatedFaq() {
  return <div className={styles.faqRows}>{questions.map(([question, answer]) => <FaqRow key={question} question={question} answer={answer} />)}</div>;
}
