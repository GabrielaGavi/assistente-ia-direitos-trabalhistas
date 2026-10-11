# ADR-0004: Banco PostgreSQL para testes de integração

**Status:** Proposta — bloqueada por restrição de ambiente
**Data:** 2026-10-11
**Decisores:** Equipe do Projeto Integrador IV (turma 6HC1)
**Tarefas relacionadas:** T006 (#12), T007 (#13)
**Feature:** `001-fontes-e-rastreabilidade`

---

## Contexto

A Fase 2 (Foundational) exige fixtures assíncronas de banco (T006) e migrations
Alembic (T007). Para cumprir o Princípio III (*"sem testes, sem conclusão"*), os
testes de integração precisam rodar contra um banco real.

E precisa ser **PostgreSQL**, não um substituto. As regras centrais da feature
dependem de recursos exclusivos dele:

| Regra da especificação | Recurso exigido |
|---|---|
| No máximo uma versão ativa por `(source_id, logical_name)` | **Índice único parcial** (`WHERE is_active = true`) |
| `metadata_extra` dos chunks | Tipo **JSONB** |
| Busca híbrida das próximas features | `pgvector` + *Full Text Search* |

O índice parcial é o ponto crítico: o SQLite não o suporta na forma exigida. Testar a
unicidade de versão ativa em SQLite daria **falso verde** — o teste passaria sem
provar nada sobre o comportamento em produção. Seria pior do que não testar, porque
produziria confiança injustificada.

### Restrição de ambiente encontrada

A decisão inicial da equipe foi rodar PostgreSQL 16 em contêiner Docker local. Ao
executar, o Docker Desktop falhou:

```
Docker Engine stopped unexpectedly
vpnkit-bridge handshake failed ... WSL2 não pode ser iniciado
porque a virtualização não está habilitada
```

Diagnóstico na máquina de desenvolvimento:

```
Virtualização Habilitada no Firmware: Não
HypervisorPresent:                    False
```

A virtualização (Intel VT-x / AMD-V) está **desativada na BIOS/UEFI**. Sem ela o WSL2
não inicia, e sem WSL2 o Docker Engine não sobe no Windows. Não é defeito de
instalação — reinstalar o Docker não resolve. A correção exige reiniciar a máquina,
entrar no setup da BIOS e habilitar a virtualização.

---

## Decisão

*Pendente.* Mantém-se PostgreSQL como banco de testes — isso não está em discussão.
O que falta decidir é **como provisioná-lo** diante do bloqueio acima.

---

## Opções consideradas

### Opção A: Habilitar a virtualização na BIOS e manter o Docker

| Dimensão | Avaliação |
|----------|-----------|
| Esforço inicial | Médio (reboot + BIOS) |
| Paridade com produção | Alta |
| Impacto no restante da equipe | Nenhum |

**Prós:**
- Mantém a decisão original e o `docker-compose.yml` como fonte única do ambiente.
- Permite usar a imagem `pgvector/pgvector:pg16`, já com a extensão necessária para
  as features de RAG seguintes.
- Destrói e recria o banco em segundos, isolando a suíte de testes.
- Desbloqueia o Docker para todo o resto do projeto.

**Contras:**
- Exige reinício e acesso ao setup da BIOS, que varia por fabricante.
- Interrompe o trabalho agora.

### Opção B: PostgreSQL 16 nativo no Windows

| Dimensão | Avaliação |
|----------|-----------|
| Esforço inicial | Baixo |
| Paridade com produção | Média |
| Impacto no restante da equipe | Nenhum |

**Prós:**
- Dispensa virtualização: desbloqueia os testes **imediatamente**
  (`winget install PostgreSQL.PostgreSQL.16`).
- Suporta índice parcial, JSONB e `uuid-ossp` — tudo o que a feature 001 precisa.

**Contras:**
- Instalar `pgvector` nativamente no Windows é trabalhoso (exige compilação). Vira
  problema nas features de RAG, não nesta.
- Serviço permanente na máquina, consumindo recursos.
- Ambiente menos descartável: limpar o estado entre execuções é manual.

### Opção C: Neon na nuvem

| Dimensão | Avaliação |
|----------|-----------|
| Esforço inicial | Baixo |
| Paridade com produção | Máxima |
| Impacto no restante da equipe | Alto (compartilhado) |

**Prós:**
- É o banco de produção previsto no plano; paridade total, `pgvector` incluso.
- Nada a instalar.

**Contras:**
- Testes passam a depender de internet e ficam sensivelmente mais lentos — latência
  de rede a cada transação, em uma suíte que roda dezenas de vezes por dia em TDD.
- Risco de integrantes compartilharem a mesma instância e um teste destrutivo
  derrubar o trabalho de outro.
- Consome cota do plano gratuito.

### Opção D: SQLite nos testes

**Descartada.** Não suporta o índice único parcial que expressa a regra de negócio
central da feature. Produziria falso verde no teste mais importante — violação direta
do Princípio III.

---

## Análise de trade-offs

O eixo é **velocidade de desbloqueio** contra **paridade com produção**.

A Opção B desbloqueia hoje, mas empurra o problema do `pgvector` para a feature de
RAG — onde ele será inevitável. A Opção A custa uma interrupção agora e resolve
`pgvector`, isolamento e Docker de uma vez. A Opção C evita instalar qualquer coisa,
mas troca um problema pontual por lentidão permanente no ciclo de TDD.

Recomendação: **Opção A**, com a **Opção B como alternativa** caso a BIOS da máquina
não ofereça a configuração ou o reboot não seja conveniente agora. As duas são
compatíveis — habilitar a virtualização depois não invalida uma instalação nativa.

---

## Consequências

**Se Opção A:**
- Docker fica disponível para todo o projeto (banco, futura imagem do backend, CI local).
- Custo de uma interrupção pontual.

**Se Opção B:**
- Testes desbloqueados imediatamente.
- A dívida do `pgvector` precisará ser paga antes da feature de busca híbrida.

**Precisa ser revisitado:**
- Ao chegar na feature de RAG, confirmar que o ambiente escolhido oferece `pgvector`.
- Ao configurar CI, usar o serviço `postgres` do GitHub Actions, independente da
  escolha local.

---

## Itens de ação

1. [ ] Decidir entre Opção A e Opção B.
2. [ ] Provisionar o PostgreSQL 16 e registrar a `DATABASE_URL` em `.env.example`.
3. [ ] Implementar as fixtures assíncronas com rollback por teste (T006).
4. [ ] Inicializar o Alembic e gerar a primeira migration (T007).
5. [ ] Atualizar o status deste ADR para *Aceita* registrando a opção escolhida.
