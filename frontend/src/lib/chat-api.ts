/** Contratos de app/auth, app/conversations e app/citations do FastAPI. */
export type User = { id: string; name: string; email: string; role: string; is_active: boolean };
export type AnonymousSession = { questions_used: number; questions_limit: number; expires_at: string };
export type Citation = { id: string; citation_number: number; original_quote: string };
export type Message = {
  id: string;
  role: "USER" | "ASSISTANT";
  status: "COMPLETED" | "FAILED";
  content: string;
  created_at: string;
  citations: Citation[];
};
export type Conversation = { id: string; title: string; created_at: string; updated_at: string };
export type ConversationPage = { items: Conversation[]; total: number };
export type ConversationDetail = Conversation & { messages: Message[] };
export type CitationDetail = Citation & {
  chunk: { official_url: string; article: string | null; section: string | null; paragraph: string | null };
  source: { name: string; short_name: string; base_url: string };
};

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

export async function chatApi<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api/backend/${path}`, {
      ...options,
      credentials: "same-origin",
      cache: "no-store",
      headers: { "Content-Type": "application/json", ...options.headers },
    });
  } catch {
    throw new ApiError(0, "Não foi possível conectar. Confira sua conexão e tente novamente.");
  }
  const data = await response.json().catch(() => null);
  if (!response.ok) throw new ApiError(response.status, data?.detail ?? "Não foi possível concluir a solicitação.");
  return data as T;
}
