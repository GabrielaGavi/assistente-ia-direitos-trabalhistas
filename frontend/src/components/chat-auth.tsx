"use client";

import { useState, type FormEvent } from "react";
import { chatApi, type User } from "@/lib/chat-api";
import styles from "./chat-shell.module.css";

export function ChatAuth({ onAuthenticated }: { onAuthenticated: (user: User) => void }) {
  const [register, setRegister] = useState(false);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState("");

  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (pending) return;
    const form = new FormData(event.currentTarget);
    const password = String(form.get("password") ?? "");
    if (new TextEncoder().encode(password).length > 72) {
      setError("A senha deve ter no máximo 72 bytes. Acentos e emojis ocupam mais de um byte.");
      return;
    }
    setPending(true); setError("");
    try {
      const user = await chatApi<User>(`auth/${register ? "register" : "login"}`, {
        method: "POST",
        body: JSON.stringify({ email: String(form.get("email")).trim(), password,
          ...(register ? { name: String(form.get("name")).trim() } : {}) }),
      });
      onAuthenticated(user);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Não foi possível entrar.");
    } finally { setPending(false); }
  }

  return <section className={styles.auth} aria-labelledby="chat-auth-title">
    <p className={styles.eyebrow}>[ SUA CONTA, SUAS CONVERSAS ]</p>
    <h1 id="chat-auth-title">{register ? "Crie sua conta." : "Entre na sua conta."}</h1>
    <p className={styles.lead}>Você pode começar sem cadastro. Entre para continuar após o limite gratuito e guardar suas conversas, sem perder o que já perguntou.</p>
    <form onSubmit={submit} className={styles.authForm}>
      <fieldset disabled={pending}>
        {register && <label>Como podemos chamar você?<input name="name" autoComplete="name" required maxLength={255} /></label>}
        <label>E-mail<input name="email" type="email" autoComplete="email" required maxLength={254} /></label>
        <label>Senha<input key={register ? "new" : "current"} name="password" type="password" autoComplete={register ? "new-password" : "current-password"} required minLength={register ? 8 : 1} maxLength={72} /></label>
        {register && <p className={styles.fieldHint}>Use pelo menos 8 caracteres.</p>}
        {error && <p role="alert" className={styles.error}>{error}</p>}
        <button className={styles.action} type="submit">{pending ? "Aguarde…" : register ? "Criar conta" : "Entrar"}<span aria-hidden="true">↗</span></button>
      </fieldset>
    </form>
    <button disabled={pending} className={styles.textButton} onClick={() => { setRegister(value => !value); setError(""); }}>{register ? "Já tenho conta. Entrar" : "Ainda não tenho conta. Cadastrar"}</button>
  </section>;
}
