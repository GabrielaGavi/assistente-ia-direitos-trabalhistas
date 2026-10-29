import Link from "next/link";
import { ComparisonIllustration } from "./comparison-illustration";

const topics = ["Férias", "13º salário", "Jornada e horas extras", "Aviso-prévio", "FGTS", "Rescisão do contrato"];

export function DireitoContent() {
  return (
    <div className="direitoContent">
      <section className="direitoSection direitoIntro" id="principios">
        <p className="direitoEyebrow">PROPÓSITO</p>
        <h2>Informação trabalhista que começa pela fonte.</h2>
        <p className="direitoLead">Direito em Claro ajuda você a organizar uma dúvida, entender termos e localizar referências oficiais. Não substitui atendimento jurídico.</p>
        <div className="direitoCards">
          <article><span>01</span><h3>Fontes verificáveis</h3><p>A resposta deve apontar a norma ou o documento que sustenta a explicação.</p></article>
          <article><span>02</span><h3>Linguagem direta</h3><p>Textos técnicos são apresentados com contexto, sem esconder os limites da informação.</p></article>
          <article><span>03</span><h3>Uso responsável</h3><p>Quando faltar evidência ou for necessário apoio profissional, isso precisa ficar claro.</p></article>
        </div>
      </section>

      <section className="direitoSection direitoComparison" id="comparacao">
        <p className="direitoEyebrow">TRANSPARÊNCIA</p>
        <h2>Antes de decidir, saiba de onde vem a informação.</h2>
        <p className="direitoLead">Uma resposta útil não é um palpite: ela explica o assunto, mostra o que foi consultado e indica quando procurar atendimento especializado.</p>
        <div className="direitoComparisonGrid">
          <article className="direitoComparisonCard"><ComparisonIllustration kind="guidance" label="Resposta genérica" /><h3>Resposta sem fonte</h3><p>Pode simplificar a dúvida, mas não permite conferir a base da orientação.</p></article>
          <article className="direitoComparisonCard direitoComparisonCard--highlight"><div className="direitoMark" aria-hidden="true">✣</div><h3>Direito em Claro</h3><p>Organiza a pergunta, apresenta a explicação em linguagem simples e mantém a referência visível.</p></article>
          <article className="direitoComparisonCard"><ComparisonIllustration kind="research" label="Busca isolada" /><h3>Pesquisa solta</h3><p>Encontrar uma regra não basta: é preciso entender a situação e a origem daquele conteúdo.</p></article>
        </div>
      </section>

      <section className="direitoSection direitoSteps" id="como-funciona">
        <p className="direitoEyebrow">COMO FUNCIONA</p>
        <h2>Uma conversa para transformar dúvida em próximo passo.</h2>
        <div className="direitoStepsGrid">
          <article><b>01</b><h3>Conte o que aconteceu</h3><p>Escreva a situação com suas palavras, sem precisar conhecer termos jurídicos.</p></article>
          <article><b>02</b><h3>Leia a orientação</h3><p>A resposta separa explicação, limites e pontos que podem exigir mais informação.</p></article>
          <article><b>03</b><h3>Confira a fonte</h3><p>Use as referências para consultar o material original e se preparar para buscar ajuda.</p></article>
        </div>
      </section>

      <section className="direitoSection direitoTopics" id="recursos">
        <p className="direitoEyebrow">TEMAS INICIAIS</p>
        <h2>Dúvidas comuns, tratadas com cuidado.</h2>
        <p className="direitoLead">A ferramenta foi pensada para perguntas iniciais sobre direitos trabalhistas. A cobertura depende dos documentos disponíveis na base.</p>
        <div className="direitoTopicList">{topics.map((topic) => <span key={topic}>{topic}</span>)}</div>
      </section>

      <section className="direitoSection direitoLimits" id="limites">
        <p className="direitoEyebrow">LIMITES IMPORTANTES</p>
        <h2>Informação não é parecer jurídico.</h2>
        <p className="direitoLead">Situações com prazo, documentos, cálculos, risco imediato ou conflito precisam de análise profissional. Procure sindicato, Ministério do Trabalho, Defensoria Pública ou advogado quando necessário.</p>
      </section>

      <section className="direitoSection direitoFaq" id="duvidas">
        <p className="direitoEyebrow">DÚVIDAS FREQUENTES</p>
        <h2>Use com consciência.</h2>
        <details><summary>O assistente substitui advogado ou sindicato?</summary><p>Não. Ele oferece informação educativa e referências; não analisa provas nem emite parecer jurídico.</p></details>
        <details><summary>Posso confiar em qualquer resposta?</summary><p>Confira as fontes citadas e considere o contexto do seu caso. Uma resposta sem evidência suficiente deve ser tratada como limite, não como conclusão.</p></details>
        <details><summary>Que dados devo compartilhar?</summary><p>Evite dados pessoais sensíveis. Descreva a situação sem enviar documentos, senhas, números de identificação ou informações de terceiros.</p></details>
        <details><summary>Quais assuntos posso perguntar?</summary><p>Férias, 13º, jornada, horas extras, aviso-prévio, FGTS e rescisão são exemplos de temas iniciais.</p></details>
      </section>

      <section className="direitoCta" id="comecar">
        <p className="direitoEyebrow">COMECE POR UMA DÚVIDA</p>
        <h2>O que aconteceu no seu trabalho?</h2>
        <p>Conte a situação de forma simples. A interface reforça que a orientação é informativa e que as fontes precisam ser conferidas.</p>
        <Link href="/chat">Abrir assistente <span>↗</span></Link>
      </section>
    </div>
  );
}
