import Link from "next/link";
import { ContextGraph } from "./context-graph";
import { KnowledgeSphere } from "./graph-effects";
import { ProjectArchitecture } from "./project-architecture";
import { LandingMotion } from "./landing-motion";
import { AnimatedFaq } from "./animated-faq";
import { chatTopics, topicChatUrl } from "@/lib/chat-topics";
import styles from "./direito-site.module.css";

export function DireitoSite() {
  return <main className={styles.page}>
    <header className={styles.header}>
      <Link href="#inicio" className={styles.brand}><span className={styles.brandMark} aria-hidden="true"><i /><i /><i /><i /></span>Direito em Claro</Link>
      <nav aria-label="Navegação principal"><a href="#contexto">Conhecimento</a><a href="#arquitetura">Arquitetura</a><a href="#temas">Temas</a><a href="#duvidas">Dúvidas</a></nav>
      <Link href="/chat" className={styles.headerCta}>Abrir assistente <span aria-hidden="true">↗</span></Link>
    </header>
    <ContextGraph />
    <section className={styles.knowledge} id="contexto">
      <h2 data-reveal>Conhecimento conectado à sua dúvida.</h2>
      <div className={styles.knowledgeFrame}>
        <div className={styles.knowledgeTop}>
          <div className={styles.knowledgeCopy} data-reveal><h3>Encontre<br />o que importa.</h3><p>Normas, documentos e trechos ganham contexto para ajudar você a entender uma situação trabalhista e conferir a origem da informação.</p><span className={styles.smallCaption}>PERGUNTA → CONTEXTO → EVIDÊNCIA</span></div>
          <div className={styles.sphereStage}><KnowledgeSphere className={styles.sphere} /><span className={styles.sphereCaption}>Explore as conexões com o cursor</span></div>
        </div>
        <div className={styles.featureGrid}>
          <article><div className={styles.featureCopy}><h3>Referências verificáveis</h3><p>Uma explicação deve permitir voltar à fonte e ao trecho que a sustenta.</p></div><div className={styles.referenceVisual} aria-hidden="true"><div><strong>FONTE</strong><span>Origem preservada</span></div></div></article>
          <article><div className={styles.featureCopy}><h3>Contexto em camadas</h3><p>Fonte, documento e evidência. Cada parte mantém o seu lugar na orientação.</p></div><div className={styles.layersVisual} aria-hidden="true"><div className={styles.isoGrid} /><span>Fonte</span><span>Documento</span><span>Trecho</span></div></article>
          <article><div className={styles.featureCopy}><h3>Clareza em cada etapa</h3><p>Entenda o caminho entre sua pergunta e as referências apresentadas.</p><span className={styles.featureAccent}>perguntar → conferir</span></div><div className={styles.trackVisual} aria-hidden="true">{Array.from({ length: 7 }, (_, index) => <span key={index}><i /></span>)}</div></article>
        </div>
      </div>
    </section>
    <ProjectArchitecture />
    <section className={styles.topics} id="temas"><div className={styles.sectionHeading} data-reveal><h2>Dúvidas do dia a dia.</h2><p>Escolha um assunto. Sua pergunta já chega preparada no assistente para você completar com o que aconteceu.</p></div><div className={styles.topicList}>{chatTopics.map((topic, i) => <Link href={topicChatUrl(topic)} key={topic.id}><span>0{i + 1}</span><h3>{topic.label}</h3><small>Começar por este tema</small><i aria-hidden="true">↗</i></Link>)}</div></section>
    <section className={styles.faq} id="duvidas"><div className={styles.sectionHeading} data-reveal><h2>Antes de começar.</h2><p>O papel da ferramenta e os cuidados que fazem parte de uma boa orientação.</p></div><AnimatedFaq /></section>
    <section className={styles.finalCta}><p>INFORMAÇÃO PARA O PRÓXIMO PASSO</p><h2>Sua dúvida tem contexto.<br />Vamos começar por ele.</h2><Link href="/chat">Abrir assistente <span aria-hidden="true">↗</span></Link></section>
    <footer className={styles.footer}><Link href="#inicio" className={styles.brand}>Direito em Claro</Link><p>Projeto acadêmico · orientação trabalhista informativa</p><a href="#arquitetura">Arquitetura ↑</a></footer>
    <LandingMotion />
  </main>;
}
