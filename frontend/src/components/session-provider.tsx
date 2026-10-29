"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import { ApiError, chatApi, type AnonymousSession, type User } from "@/lib/chat-api";
import { ChatAuth } from "./chat-auth";
import styles from "./session-provider.module.css";
import headerAction from "./header-action.module.css";

type Session = {
  user: User | null; checking: boolean;
  openLogin: () => void;
  authenticated: (user: User) => void;
  logout: () => Promise<void>;
  expired: () => void;
  startAnonymous: () => Promise<AnonymousSession>;
};
const SessionContext = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [checking, setChecking] = useState(true);
  const [open, setOpen] = useState(false);
  const [sessionError, setSessionError] = useState("");
  const dialog = useRef<HTMLDialogElement>(null);
  const guestRequest = useRef<Promise<AnonymousSession> | null>(null);
  useEffect(() => {
    let active = true;
    chatApi<User>("auth/session").then(value => { if (active) setUser(value); }).catch(reason => {
      if (active && !(reason instanceof ApiError && reason.status === 401)) setSessionError(reason.message);
    }).finally(() => { if (active) setChecking(false); });
    return () => { active = false; };
  }, []);
  useEffect(() => {
    if (open) dialog.current?.showModal();
    else dialog.current?.close();
  }, [open]);
  const authenticated = useCallback((value: User) => { setUser(value); setOpen(false); setSessionError(""); }, []);
  const expired = useCallback(() => setUser(null), []);
  const startAnonymous = useCallback(() => {
    if (!guestRequest.current) {
      guestRequest.current = chatApi<AnonymousSession>("auth/anonymous", { method: "POST", body: "{}" })
        .finally(() => { guestRequest.current = null; });
    }
    return guestRequest.current;
  }, []);
  const logout = useCallback(async () => {
    await chatApi("auth/session", { method: "DELETE" });
    setUser(null);
  }, []);
  return <SessionContext.Provider value={{ user, checking, openLogin: () => setOpen(true), authenticated, logout, expired, startAnonymous }}>
    {children}
    <dialog ref={dialog} className={styles.dialog} aria-labelledby="chat-auth-title" onCancel={() => setOpen(false)} onClose={() => setOpen(false)} data-lenis-prevent>
      <div className={styles.panel}>
        <button className={styles.close} aria-label="Fechar acesso à conta" onClick={() => setOpen(false)}>×</button>
        {open && <><ChatAuth onAuthenticated={authenticated} />{sessionError && <p role="alert" className={styles.error}>{sessionError}</p>}</>}
      </div>
    </dialog>
  </SessionContext.Provider>;
}

export function useSession() {
  const session = useContext(SessionContext);
  if (!session) throw new Error("SessionProvider ausente.");
  return session;
}

export function AccountButton({ disabled, onLogout }: { disabled?: boolean; onLogout?: () => Promise<boolean> }) {
  const session = useSession();
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");
  async function logout() {
    setPending(true); setError("");
    try { if (onLogout) await onLogout(); else await session.logout(); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Não foi possível sair."); }
    finally { setPending(false); }
  }
  return <div className={styles.account}>
    {session.user ? <><span title={session.user.name}>{session.user.name}</span><button className={headerAction.action} disabled={disabled || pending} onClick={() => void logout()}>{pending ? "Saindo…" : "Sair"}</button></> : <button className={headerAction.action} disabled={disabled || session.checking} onClick={session.openLogin}>Entrar <span aria-hidden="true">↗</span></button>}
    {error && <span role="alert" className={styles.error}>{error}</span>}
  </div>;
}
