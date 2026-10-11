-- Extensoes exigidas pelo plano tecnico, aplicadas aos dois bancos.
--
--   uuid-ossp : utilitarios de UUID no lado do banco. Os IDs do dominio sao
--               gerados na aplicacao em UUID v7 (ver ADR-0001); esta extensao
--               cobre geracao pontual em migrations e seeds.
--   vector    : busca vetorial (pgvector), exigida pela busca hibrida do RAG.

\connect assistente_trabalhista
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

\connect assistente_trabalhista_test
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;
