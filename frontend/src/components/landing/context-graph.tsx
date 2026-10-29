"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { PixelField } from "./graph-effects";
import styles from "./direito-site.module.css";

type LabelBox = { x: number; y: number; width: number; height: number };
const edges = [[0,1],[1,2],[0,3],[1,4],[2,5],[3,6],[4,7],[5,8],[6,7],[7,8]];

function connect(a: LabelBox, b: LabelBox) {
  const sameRow = Math.abs(a.y - b.y) < 4;
  if (sameRow) {
    const left = a.x < b.x ? a : b, right = a.x < b.x ? b : a;
    const y = left.y + left.height / 2;
    return `M${left.x + left.width + 12},${y}H${right.x - 12}`;
  }
  const upper = a.y < b.y ? a : b, lower = a.y < b.y ? b : a;
  const x1 = upper.x + upper.width / 2, x2 = lower.x + lower.width / 2;
  const y1 = upper.y + upper.height + 10, y2 = lower.y - 10;
  const middle = (y1 + y2) / 2;
  return `M${x1},${y1}V${middle}H${x2}V${y2}`;
}

export function ContextGraph() {
  const [graph, setGraph] = useState(false);
  const content = useRef<HTMLDivElement>(null);
  const prose = useRef<HTMLDivElement>(null);
  const svg = useRef<SVGSVGElement>(null);
  const lines = useRef<SVGPathElement>(null);

  useEffect(() => {
    const root = content.current, text = prose.current;
    if (!root || !text) return;
    let active = true;
    const measure = () => {
      const area = root.getBoundingClientRect();
      const nodes = Array.from(root.querySelectorAll<HTMLElement>("[data-node]"));
      const labels = nodes.map(node => {
        const label = node.firstElementChild as HTMLElement;
        return { width: label.offsetWidth, height: label.offsetHeight };
      });
      const horizontalGap = area.width < 480 ? 24 : 32;
      const rowGap = area.width < 480 ? 34 : 58;
      const rows: number[][] = [];
      let row: number[] = [], used = 0;
      labels.forEach((label, index) => {
        if (row.length && (row.length === 3 || used + horizontalGap + label.width > area.width - 12)) {
          rows.push(row); row = []; used = 0;
        }
        used += (row.length ? horizontalGap : 0) + label.width;
        row.push(index);
      });
      if (row.length) rows.push(row);
      const layout: LabelBox[] = [];
      let y = 18;
      rows.forEach(indices => {
        const width = indices.reduce((sum, index) => sum + labels[index].width, 0);
        const gap = indices.length === 1 ? 0 : Math.min(58, (area.width - width - 12) / (indices.length - 1));
        let x = (area.width - width - gap * (indices.length - 1)) / 2;
        indices.forEach(index => {
          layout[index] = { x, y, ...labels[index] };
          x += labels[index].width + gap;
        });
        y += Math.max(...indices.map(index => labels[index].height)) + rowGap;
      });
      // Both modes keep the exact same font metrics and reserve the same area.
      // Only positions, connective prose and graph lines animate on toggles.
      const minimumHeight = Number.parseFloat(getComputedStyle(root).minHeight) || 330;
      const height = Math.ceil(Math.max(text.offsetHeight, y - rowGap + 25, minimumHeight));
      if (root.style.height !== `${height}px`) root.style.height = `${height}px`;
      nodes.forEach((node, index) => {
        const origin = node.getBoundingClientRect();
        node.style.setProperty("--dx", `${layout[index].x - (origin.left - area.left)}px`);
        node.style.setProperty("--dy", `${layout[index].y - (origin.top - area.top)}px`);
      });
      svg.current?.setAttribute("viewBox", `0 0 ${area.width} ${height}`);
      lines.current?.setAttribute("d", edges.map(([a,b]) => connect(layout[a], layout[b])).join(" "));
    };
    const observer = new ResizeObserver(measure);
    observer.observe(root); observer.observe(text); measure();
    void document.fonts.ready.then(() => { if (active) measure(); });
    return () => { active = false; observer.disconnect(); };
  }, []);

  const node = (index: number, text: string) => <span data-node={index} className={styles.phraseSlot}><span className={styles.phrase}>{text}</span></span>;

  return <section className={styles.hero} id="inicio">
    <div className={styles.heroInner}>
      <div className={styles.heroCopy}>
        <h1>Entenda seus direitos com contexto, clareza e fontes.</h1>
        <div className={styles.modeToggle} role="group" aria-label="Visualização do conteúdo">
          <button type="button" aria-pressed={!graph} onClick={() => setGraph(false)}>Texto</button>
          <button type="button" aria-pressed={graph} onClick={() => setGraph(true)}>Grafo</button>
        </div>
        <div ref={content} className={`${styles.morphContent} ${graph ? styles.graphMode : ""}`}>
          <svg ref={svg} className={styles.morphLines} aria-hidden="true"><path ref={lines} /></svg>
          <div ref={prose}>
            <p>{node(0,"Direito em Claro")}<span className={styles.connector}> conecta </span>{node(1,"sua pergunta")}<span className={styles.connector}> a </span>{node(2,"fontes oficiais")}<span className={styles.connector}>, relacionando </span>{node(3,"fatos e contexto")}<span className={styles.connector}>, </span>{node(4,"temas trabalhistas")}<span className={styles.connector}> e </span>{node(5,"trechos de documentos")}<span className={styles.connector}> para explicar o que importa na sua situação.</span></p>
            <p><span className={styles.connector}>O objetivo é construir </span>{node(6,"orientação acessível")}<span className={styles.connector}>, com </span>{node(7,"referências verificáveis")}<span className={styles.connector}> e </span>{node(8,"limites explícitos")}<span className={styles.connector}>. Informação para começar com mais clareza e saber quando buscar apoio profissional.</span></p>
          </div>
        </div>
        <div className={styles.actions}><Link href="/chat">Fazer uma pergunta <span aria-hidden="true">↗</span></Link><a href="#arquitetura">Explorar a arquitetura <span aria-hidden="true">↓</span></a></div>
      </div>
      <div className={styles.heroVisual} role="img" aria-label="Pixels em movimento formam o rosto e o pescoço de uma estátua até a borda da seção">
        <PixelField className={styles.pixelField} />
      </div>
    </div>
  </section>;
}
