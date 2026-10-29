"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError, chatApi, type AnonymousSession, type Conversation, type ConversationPage, type ConversationDetail, type Message } from "./chat-api";
import { useSession } from "@/components/session-provider";

export function useChat() {
  const { user, checking: sessionChecking, expired: endSession, logout: endAccount, startAnonymous } = useSession();
  const [anonymous, setAnonymous] = useState<AnonymousSession | null>(null);
  const [attempt, setAttempt] = useState(0);
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversation, setConversation] = useState<Conversation | null>(null);
  const [history, setHistory] = useState<Conversation[]>([]);
  const [total, setTotal] = useState(0);
  const [historyError, setHistoryError] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyBusy, setHistoryBusy] = useState(false);
  const [syncRequired, setSyncRequired] = useState(false);
  const lock = useRef(false);
  const historyLock = useRef(false);
  const epoch = useRef(0);
  const invalidate = useCallback(() => { epoch.current++; }, []);

  const expire = useCallback((reason: unknown) => {
    if (reason instanceof ApiError && reason.status === 401) {
      epoch.current++;
      endSession(); setAnonymous(null); setMessages([]); setConversation(null); setHistory([]); setTotal(0);
      setError(reason.message); setSyncRequired(false);
      return true;
    }
    return false;
  }, [endSession]);

  useEffect(() => {
    if (sessionChecking) return;
    let active = true;
    const current = epoch.current;
    async function initialize() {
      if (!user) {
        const guest = await startAnonymous();
        if (!active || current !== epoch.current) return;
        setAnonymous(guest);
      }
      const page = await chatApi<ConversationPage>("conversations?offset=0&limit=20");
      if (active && current === epoch.current) {
        setHistory(previous => [...previous, ...page.items.filter(item => !previous.some(old => old.id === item.id))]);
        setTotal(previous => Math.max(previous, page.total)); setHistoryError(""); setError("");
      }
    }
    initialize().catch(reason => {
      if (active && current === epoch.current && !expire(reason)) setError(reason.message);
    });
    return () => { active = false; invalidate(); };
  }, [user, sessionChecking, attempt, expire, invalidate, startAnonymous]);

  async function loadHistory(more = false) {
    if (historyLock.current) return;
    historyLock.current = true; setHistoryBusy(true);
    const current = epoch.current;
    try {
      const page = await chatApi<ConversationPage>(`conversations?offset=${more ? history.length : 0}&limit=20`);
      if (current !== epoch.current) return;
      setHistory(previous => more ? [...previous, ...page.items.filter(item => !previous.some(old => old.id === item.id))] : page.items);
      setTotal(page.total); setHistoryError("");
    } catch (reason) {
      if (current === epoch.current && !expire(reason)) setHistoryError(reason instanceof Error ? reason.message : "Não foi possível carregar o histórico.");
    } finally { historyLock.current = false; setHistoryBusy(false); }
  }

  async function open(id: string) {
    if (lock.current) return;
    lock.current = true; setBusy(true); setError("");
    const current = epoch.current;
    try {
      const detail = await chatApi<ConversationDetail>(`conversations/${id}`);
      if (current !== epoch.current) return;
      setConversation(detail); setMessages(detail.messages); setSyncRequired(false);
    } catch (reason) {
      if (current === epoch.current && !expire(reason)) setError(reason instanceof Error ? reason.message : "Não foi possível abrir a conversa.");
    } finally { lock.current = false; setBusy(false); }
  }

  async function send(question: string): Promise<boolean> {
    if (lock.current || (!user && !anonymous) || syncRequired || !question.trim() || question.length > 4000) return false;
    if (!user && anonymous && anonymous.questions_used >= anonymous.questions_limit) {
      setError("Você usou as perguntas sem conta. Use Entrar no topo para continuar sem perder a conversa.");
      return false;
    }
    lock.current = true; setBusy(true); setError("");
    const current = epoch.current;
    let target = conversation;
    try {
      if (!target) {
        target = await chatApi<Conversation>("conversations", { method: "POST", body: JSON.stringify({ title: question.slice(0, 100) }) });
        if (current !== epoch.current) return false;
        setConversation(target);
        const created = target;
        setHistory(previous => [created, ...previous]); setTotal(value => value + 1);
      }
      setMessages(previous => [...previous, { id: `local-${crypto.randomUUID()}`, role: "USER", status: "COMPLETED", content: question, created_at: new Date().toISOString(), citations: [] }]);
      const answer = await chatApi<Message>(`conversations/${target.id}/messages`, { method: "POST", body: JSON.stringify({ content: question }) });
      if (current !== epoch.current) return false;
      setMessages(previous => [...previous, answer]);
      return true;
    } catch (reason) {
      if (current !== epoch.current || expire(reason)) return false;
      setError(reason instanceof Error ? reason.message : "Não foi possível enviar a pergunta.");
      // O backend persiste a pergunta antes de chamar a IA, inclusive quando ela falha.
      // Reconcilie o histórico, sem repetir o POST e duplicar a pergunta.
      if (target) {
        try {
          const detail = await chatApi<ConversationDetail>(`conversations/${target.id}`);
          if (current === epoch.current) {
            setMessages(detail.messages);
            const saved = detail.messages.length > messages.length && detail.messages.some((message, index) => index >= messages.length && message.role === "USER" && message.content === question);
            const settled = saved && detail.messages.at(-1)?.role === "ASSISTANT";
            setSyncRequired(!settled && reason instanceof ApiError && [0, 503, 504].includes(reason.status));
            return saved;
          }
        } catch (syncError) {
          if (current === epoch.current && !expire(syncError)) setSyncRequired(true);
        }
      }
      return false;
    } finally {
      if (!user && current === epoch.current) {
        try {
          const guest = await startAnonymous();
          if (current === epoch.current) setAnonymous(guest);
        } catch { /* O erro do envio permanece visivel; o servidor continua controlando a quota. */ }
      }
      lock.current = false; setBusy(false);
    }
  }

  function reset() {
    if (lock.current) return false;
    setConversation(null); setMessages([]); setError(""); setSyncRequired(false);
    if (!user && !anonymous) setAttempt(value => value + 1);
    return true;
  }

  async function logout() {
    if (lock.current) return false;
    lock.current = true; setBusy(true);
    try {
      await endAccount();
      epoch.current++; setAnonymous(null); setMessages([]); setConversation(null); setHistory([]); setTotal(0); setError(""); setHistoryError(""); setSyncRequired(false);
      return true;
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Não foi possível sair."); return false; }
    finally { lock.current = false; setBusy(false); }
  }

  const checking = sessionChecking || (!user && !anonymous && !error);
  const remaining = anonymous ? Math.max(0, anonymous.questions_limit - anonymous.questions_used) : 0;
  return { user, checking, anonymous, remaining, messages, conversation, history, total, error, busy, historyBusy, historyError, syncRequired, open, send, reset, logout, loadHistory, retrySession: () => { setError(""); setAttempt(value => value + 1); } };
}
