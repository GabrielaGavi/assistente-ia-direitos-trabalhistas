"use client";

import { useState } from "react";
import styles from "./direito-site.module.css";

const stages = [
  { title: "Interface de conversa", technology: "React · Next.js · TypeScript", description: "A camada de apresentação recebe a pergunta e exibe a resposta. O chat atual é uma demonstração; a conexão com o fluxo de geração ainda será integrada." },
  { title: "API e regras de domínio", technology: "FastAPI · Pydantic · SQLAlchemy", description: "Routers, serviços e repositórios separam transporte HTTP, regras e persistência. Fontes, documentos, trechos e citações já têm módulos próprios no backend." },
  { title: "Base rastreável", technology: "PostgreSQL · DocumentChunk · Citation", description: "Cada trecho preserva sua origem e versão documental. As citações ligam a evidência ao documento e à fonte, permitindo conferir a procedência." },
  { title: "Recuperação e geração", technology: "RAG · embeddings · Llama / Groq", description: "No fluxo planejado, a busca semântica recupera trechos relacionados à pergunta e o modelo produz uma explicação apoiada nesse contexto. Esta etapa ainda está prevista." },
];

export function ProjectArchitecture() {
  const [selected, setSelected] = useState(0);
  return <section className={styles.architecture} id="arquitetura">
    <div className={styles.sectionHeading} data-reveal><h2>Arquitetura</h2><p>Da pergunta à evidência: uma interface acessível, uma API modular e documentos com origem preservada.</p></div>
    <div className={styles.architectureLayout}>
      <div className={styles.blueprint}>
        <div className={styles.diagramLabel}><span>VISÃO DO SISTEMA</span><span>01—04</span></div>
        <div className={styles.userNode}><span aria-hidden="true">◎</span> Pessoa usuária</div>
        <div className={styles.verticalConnector}><i /></div>
        <button className={`${styles.archNode} ${selected === 0 ? styles.selectedNode : ""}`} onClick={() => setSelected(0)} aria-pressed={selected === 0}><span>01</span><strong>Interface web</strong><small>React / Next.js</small></button>
        <div className={styles.verticalConnector}><i /></div>
        <button className={`${styles.archNode} ${selected === 1 ? styles.selectedNode : ""}`} onClick={() => setSelected(1)} aria-pressed={selected === 1}><span>02</span><strong>API de aplicação</strong><small>FastAPI / serviços / repositórios</small></button>
        <div className={styles.forkConnector} aria-hidden="true"><i /><i /></div>
        <div className={styles.domainNodes}>
          <div><b>FONTES</b><small>origem oficial</small></div><div><b>DOCUMENTOS</b><small>versões e trechos</small></div><div><b>CITAÇÕES</b><small>evidência pública</small></div>
        </div>
        <div className={styles.verticalConnector}><i /></div>
        <button className={`${styles.archNode} ${styles.storageNode} ${selected === 2 ? styles.selectedNode : ""}`} onClick={() => setSelected(2)} aria-pressed={selected === 2}><span>03</span><strong>PostgreSQL</strong><small>dados / documentos / rastreabilidade</small></button>
        <div className={styles.plannedLane}>
          <button className={`${styles.archNode} ${selected === 3 ? styles.selectedNode : ""}`} onClick={() => setSelected(3)} aria-pressed={selected === 3}><span>04</span><strong>Recuperação → geração</strong><small>embeddings / busca / LLM</small><em>PLANEJADO</em></button>
        </div>
      </div>
      <aside className={styles.architectureDetail}>
        <span className={styles.eyebrow}>EXPLORE CADA CAMADA</span>
        <div className={styles.layerTabs} aria-label="Camadas da arquitetura">{stages.map((stage, i) => <button key={stage.title} onClick={() => setSelected(i)} aria-pressed={selected === i}>{String(i + 1).padStart(2, "0")}<span>{stage.title}</span><i>↗</i></button>)}</div>
        <div className={styles.layerDescription} key={selected}><span>CAMADA 0{selected + 1}</span><h3>{stages[selected].title}</h3><p>{stages[selected].description}</p><code>{stages[selected].technology}</code></div>
        <div className={styles.legend}><span><i /> Módulos existentes</span><span><i /> Fluxo planejado</span></div>
      </aside>
    </div>
  </section>;
}
