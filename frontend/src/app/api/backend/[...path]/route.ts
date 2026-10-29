import { NextRequest, NextResponse } from "next/server";

// O JWT fica em cookie HttpOnly. O navegador recebe somente o perfil.
const SESSION_COOKIE = "direito_session";
const ANONYMOUS_COOKIE = "direito_anonymous";
const UUID = "[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}";
const conversationPath = new RegExp(`^conversations/${UUID}$`);
const messagePath = new RegExp(`^conversations/${UUID}/messages$`);
const citationPath = new RegExp(`^citations/${UUID}$`);

function json(body: unknown, status = 200) {
  return NextResponse.json(body, { status, headers: { "Cache-Control": "no-store" } });
}

function sameOrigin(request: NextRequest) {
  try {
    const origin = new URL(request.headers.get("origin") ?? "");
    // Next pode normalizar 127.0.0.1 para localhost na URL interna.
    // Host preserva o endereço público que o navegador de fato acessou.
    return ["https:", "http:"].includes(origin.protocol) && origin.host === request.headers.get("host")?.toLowerCase();
  } catch { return false; }
}

async function handle(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path: segments } = await context.params;
  const path = segments.join("/");
  const method = request.method;
  const isAuth = method === "POST" && (path === "auth/login" || path === "auth/register");
  const isAnonymous = method === "POST" && path === "auth/anonymous";
  const isSession = path === "auth/session";
  const allowed = isAuth || isAnonymous || (isSession && ["GET", "DELETE"].includes(method)) ||
    (path === "conversations" && ["GET", "POST"].includes(method)) ||
    (method === "GET" && (conversationPath.test(path) || citationPath.test(path))) ||
    (method === "POST" && messagePath.test(path));
  if (!allowed) return json({ detail: "Endpoint não disponível." }, 404);

  // SameSite não substitui a validação de origem nas operações autenticadas.
  if (method !== "GET" && !sameOrigin(request)) {
    return json({ detail: "Origem da solicitação não permitida." }, 403);
  }
  if (isSession && method === "DELETE") {
    const response = json({ ok: true });
    response.cookies.delete(SESSION_COOKIE);
    response.cookies.delete(ANONYMOUS_COOKIE);
    return response;
  }

  const token = request.cookies.get(SESSION_COOKIE)?.value;
  const anonymousToken = request.cookies.get(ANONYMOUS_COOKIE)?.value;
  if (!isAuth && !isAnonymous && !token && (isSession || !anonymousToken)) return json({ detail: "Sua sessão expirou. Recarregue a página para continuar." }, 401);

  let body: string | undefined;
  if (method === "POST") {
    if (!request.headers.get("content-type")?.includes("application/json")) {
      return json({ detail: "Envie os dados em JSON." }, 415);
    }
    body = (await request.text()) || (isAnonymous ? "{}" : "");
    if (body.length > 20000) return json({ detail: "Solicitação muito longa." }, 413);
    try { JSON.parse(body); } catch { return json({ detail: "Dados inválidos." }, 400); }
  }

  try {
    // URL privada do servidor, nunca escolhida pelo cliente.
    const base = (process.env.BACKEND_API_URL ?? "http://127.0.0.1:8000").replace(/\/+$/, "");
    const url = new URL(`${base}/api/v1/${isSession ? "auth/me" : path}`);
    if (path === "conversations" && method === "GET") {
      for (const key of ["offset", "limit"]) {
        const value = request.nextUrl.searchParams.get(key);
        if (value !== null) url.searchParams.set(key, value);
      }
    }
    const upstream = await fetch(url, {
      method, body,
      headers: { "Content-Type": "application/json", ...(!isAuth && !isAnonymous && token ? { Authorization: `Bearer ${token}` } : {}),
        ...(anonymousToken ? { "X-Anonymous-Token": anonymousToken } : {}) },
      cache: "no-store",
      redirect: "error",
      signal: AbortSignal.timeout(messagePath.test(path) ? 120000 : 15000),
    });
    const data = await upstream.json().catch(() => null);
    if (!upstream.ok) {
      const detail = upstream.status === 422 ? "Confira os dados informados e os limites de cada campo." :
        upstream.status === 401 ? (isAuth ? "E-mail ou senha incorretos." : "Sua sessão expirou. Entre novamente para continuar.") :
        upstream.status >= 500 ? "O serviço não conseguiu concluir a solicitação. Tente novamente em instantes." :
        typeof data?.detail === "string" ? data.detail : "Não foi possível concluir a solicitação.";
      const response = json({ detail }, upstream.status);
      if (upstream.status === 401 && !isAuth) response.cookies.delete(SESSION_COOKIE);
      if (upstream.status === 401 && !isAuth && !token) response.cookies.delete(ANONYMOUS_COOKIE);
      return response;
    }
    if (isAnonymous) {
      if (typeof data?.anonymous_token !== "string" || !Number.isInteger(data.questions_used) || !Number.isInteger(data.questions_limit) || !Number.isFinite(Date.parse(data.expires_at))) {
        return json({ detail: "O serviço retornou uma sessão temporária inválida." }, 502);
      }
      const { anonymous_token: secret, ...session } = data;
      const response = json(session);
      response.cookies.set(ANONYMOUS_COOKIE, secret, {
        httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/", expires: new Date(data.expires_at),
      });
      return response;
    }
    if (isAuth) {
      if (typeof data?.access_token !== "string" || !data?.user?.id) {
        return json({ detail: "O serviço retornou uma sessão inválida." }, 502);
      }
      const response = json(data.user, upstream.status);
      response.cookies.set(SESSION_COOKIE, data.access_token, {
        httpOnly: true, sameSite: "lax", secure: process.env.NODE_ENV === "production", path: "/",
      });
      response.cookies.delete(ANONYMOUS_COOKIE);
      return response;
    }
    if (data === null) return json({ detail: "O serviço retornou uma resposta inválida." }, 502);
    return json(data, upstream.status);
  } catch (error) {
    const timeout = error instanceof Error && error.name === "TimeoutError";
    return json({ detail: timeout ? "O serviço demorou para responder. Consulte o histórico antes de enviar novamente." :
      "Não foi possível conectar ao serviço. Tente novamente em instantes." }, timeout ? 504 : 503);
  }
}

export const GET = handle;
export const POST = handle;
export const DELETE = handle;
