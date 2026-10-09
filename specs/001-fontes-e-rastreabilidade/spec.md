# Feature Specification: Fontes Jurídicas Oficiais e Rastreabilidade Documental

**Feature Branch**: `001-fontes-e-rastreabilidade`  
**Created**: 2026-10-09  
**Status**: Draft  
**Input**: User description: "Fontes jurídicas oficiais e rastreabilidade documental para o Assistente de Direitos Trabalhistas"

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Rastreabilidade de Respostas e Auditoria de Citações (Priority: P1)

Como um trabalhador que consulta o assistente sobre seus direitos,  
quero poder inspecionar a citação numérica de uma orientação e visualizar o trecho exato da legislação oficial correspondente (artigo, parágrafo e link oficial),  
para ter certeza absoluta de que a informação é legítima, vigente e verificável.

**Why this priority**: É o alicerce fundamental do produto (P0 na matriz de valor e risco). Sem a garantia de que cada citação aponta para uma fonte oficial comprovada, o assistente perde sua credibilidade ética e jurídica.

**Independent Test**: Pode ser testado de ponta a ponta simulando uma consulta fundamentada: o sistema retorna o texto acompanhado de citações numéricas `[1]`, e ao consultar o detalhe da citação, recupera o trecho original fidedigno, o artigo e a fonte oficial do Planalto.

**Acceptance Scenarios**:
1. **Given** que uma resposta ao usuário contém a citação `[1]`,  
   **When** o usuário solicita os detalhes da fonte referenciada,  
   **Then** o sistema exibe o título da norma (ex.: "CLT - Decreto-Lei nº 5.452/1943"), o artigo/seção pertinente, o trecho textual original do trecho e o link oficial governamental.
2. **Given** que um trecho legal referenciado pertence a uma versão antiga ou inativa de uma norma,  
   **When** o sistema verifica a validade da evidência para a consulta,  
   **Then** o sistema recusa a utilização do trecho desatualizado e sinaliza a necessidade de norma vigente.

---

### User Story 2 - Cadastro e Versionamento de Normas Legais pelo Administrador (Priority: P1)

Como administrador da base de conhecimento jurídica,  
quero registrar fontes oficiais (ex.: Planalto, TST, Ministério do Trabalho) e cadastrar novas normas ou atualizações da CLT com controle estrito de versão,  
para assegurar que apenas documentos validados e ativos componham o repositório de conhecimento do assistente.

**Why this priority**: Garante governança sobre o conteúdo que alimenta o sistema. Permite atualizar leis sem sobrescrever o histórico de documentos anteriormente vigentes.

**Independent Test**: O administrador cadastra a fonte "Planalto", publica o documento "CLT", e ao registrar uma nova redação legal, o sistema cria a versão v2, preservando a v1 com status inativo.

**Acceptance Scenarios**:
1. **Given** um documento cadastrado com status `READY`,  
   **When** o administrador ativa explicitamente o documento,  
   **Then** ele passa ao estado `ACTIVE` e qualquer versão anterior do mesmo documento para aquela fonte é automaticamente marcada como `INACTIVE`.
2. **Given** uma tentativa de cadastrar um documento com conteúdo idêntico (mesmo checksum) a uma versão já existente,  
   **When** o processamento é iniciado,  
   **Then** o sistema detecta a duplicidade e não cria versão redundante.

---

### User Story 3 - Consulta e Filtragem de Trechos Oficiais por Estrutura Normativa (Priority: P2)

Como administrador ou auditor do sistema,  
quero consultar os trechos divididos de um documento filtrando por artigo, seção ou capítulo,  
para auditar a qualidade da divisão estrutural antes de liberar a norma para o mecanismo de respostas.

**Why this priority**: Permite inspeção granular e garante que artigos extensos não perderam o contexto do cabeçalho ou metadados da lei.

**Independent Test**: Consultar os trechos do "Capítulo IV - Das Férias Anuais" e verificar se todos os artigos (Art. 129 a 138) possuem numeração de parágrafo e título íntegros.

**Acceptance Scenarios**:
1. **Given** um documento legal estruturado,  
   **When** o auditor filtra trechos pelo artigo "Art. 130",  
   **Then** o sistema retorna os subtrechos correspondentes, preservando o número do artigo, parágrafos, incisos e link oficial.

---

### Edge Cases

- O que acontece se uma lei for revogada expressamente?  
  O documento correspondente é alterado para `INACTIVE`, impedindo imediatamente sua recuperação para novas respostas.
- O que acontece se um trecho for referenciado por uma conversa histórica, mas a versão do documento foi substituída posteriormente?  
  A conversa histórica preserva o vínculo com o `DocumentChunk` da época em que a consulta foi realizada, garantindo auditabilidade temporal imutável.
- Como o sistema reage se a fonte oficial governamental estiver fora do ar no momento da consulta pelo usuário?  
  Os metadados locais (trecho original, artigo, título da lei e data de publicação) são exibidos integralmente, mantendo a URL oficial arquivada para consulta posterior.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE manter o registro de Fontes Oficiais (`Source`), armazenando nome da instituição, sigla, URL raiz oficial e descrição institucional.
- **FR-002**: O sistema DEVE associar todo Documento Legal (`Document`) a exatamente uma Fonte Oficial primária.
- **FR-003**: O sistema DEVE versionar documentos legais de forma imutável, registrando número de versão sequencial, checksum do conteúdo normalizado, data oficial de publicação e status do ciclo de vida (`PROCESSING`, `READY`, `FAILED`, `ACTIVE`, `INACTIVE`).
- **FR-004**: O sistema DEVE garantir que apenas uma única versão de um mesmo documento lógico esteja no estado `ACTIVE` em um dado momento.
- **FR-005**: O sistema DEVE decompor documentos em Trechos Estruturados (`DocumentChunk`), preservando metadados jurídicos essenciais: título da norma, organização emissora, artigo, parágrafo, seção, número da página (quando aplicável), índice sequencial do trecho e URL oficial.
- **FR-006**: O sistema DEVE permitir a criação de Citações (`Citation`) vinculadas estritamente a trechos de documentos (`DocumentChunk`) ativos e válidos.
- **FR-007**: As citações geradas DEVEM ser identificadas numericamente sequenciais conforme a ordem de aparição na resposta (`[1]`, `[2]`), exibindo o trecho original sem reescrita ao serem inspecionadas.
- **FR-008**: O sistema DEVE impedir a utilização de documentos inativos ou em processamento como evidência factual para o usuário.
- **FR-009**: O sistema DEVE registrar em trilha de auditoria (`AuditLog`) qualquer alteração de status administrativo de documentos (criação, ativação, desativação ou substituição de versão).

### Key Entities

- **Source (Fonte Oficial):** Representa a instituição ou repositório legal de origem (ex.: Presidência da República / Planalto, Tribunal Superior do Trabalho, Ministério do Trabalho e Emprego).
- **Document (Documento Legal):** Representa a norma jurídica propriamente dita (ex.: CLT, Lei nº 8.036/1990 do FGTS, Súmulas TST). Possui ciclo de vida, versão e checksum.
- **DocumentChunk (Trecho Normativo):** Unidade atômica de conteúdo legal com metadados estruturais (artigo, seção, parágrafo) utilizada para contextualização e citação.
- **Citation (Citação Rastreável):** Associação entre uma resposta gerada pelo assistente e o trecho documental verificado que comprova a afirmação.
- **AuditLog (Trilha de Auditoria):** Registro imutável de eventos administrativos ocorridos na base de conhecimento.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das citações apresentadas pelo assistente apontam para trechos oficiais íntegros com metadados de artigo e fonte oficial recuperáveis em menos de 100 milissegundos.
- **SC-002**: Zero ocorrências de citações apontando para documentos inativos, revogados ou órfãos no momento da resposta.
- **SC-003**: 100% das alterações administrativas de ativação/desativação de documentos registradas em trilha de auditoria verificável.
- **SC-004**: A inspeção de uma citação pelo trabalhador permite compreender o embasamento legal com clareza em menos de 10 segundos, exibindo o trecho original da lei sem necessidade de consultar fontes externas imediatas.

---

## Assumptions

- As legislações trabalhistas federais (CLT e leis complementares) são textos públicos e oficiais disponibilizados pelo portal do Planalto e órgãos oficiais do governo brasileiro.
- O cadastro e a ativação de normas na base de conhecimento são operações restritas ao papel de Administrador do sistema.
- A granularidade principal dos trechos para normas jurídicas respeita a divisão em artigos, parágrafos e incisos para maximizar a precisão da citação.
