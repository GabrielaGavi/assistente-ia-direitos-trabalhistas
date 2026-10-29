"use client";

import { useState } from "react";
import { chatApi, type Citation, type CitationDetail } from "@/lib/chat-api";
import styles from "./chat-shell.module.css";

function officialUrl(value: string) {
  try { const url = new URL(value); return ["http:", "https:"].includes(url.protocol) ? url.href : undefined; }
  catch { return undefined; }
}

export function ChatCitation({ citation }: { citation: Citation }) {
  const [detail, setDetail] = useState<CitationDetail | null>(null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  async function load() {
    if (detail || pending) return;
    setPending(true); setError("");
    try { setDetail(await chatApi<CitationDetail>(`citations/${citation.id}`)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Não foi possível consultar a fonte."); }
    finally { setPending(false); }
  }
  const url = detail ? officialUrl(detail.chunk.official_url) : undefined;
  return <details className={styles.citation} onToggle={event => { if (event.currentTarget.open) void load(); }}>
    <summary>Fonte [{citation.citation_number}] · Conferir trecho e origem</summary>
    <blockquote>{citation.original_quote}</blockquote>
    {pending && <p role="status">Consultando a origem…</p>}
    {error && <div role="alert"><p>{error}</p><button className={styles.textButton} onClick={() => void load()}>Tentar novamente</button></div>}
    {detail && <p>{detail.source.name}{detail.chunk.article ? ` · ${detail.chunk.article}` : ""}{detail.chunk.section ? ` · ${detail.chunk.section}` : ""}{detail.chunk.paragraph ? ` · ${detail.chunk.paragraph}` : ""}{url && <> · <a href={url} target="_blank" rel="noopener noreferrer">Abrir fonte oficial ↗</a></>}</p>}
  </details>;
}
