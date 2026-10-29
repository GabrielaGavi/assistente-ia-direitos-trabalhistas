import assert from "node:assert/strict";
import { createServer } from "node:http";
import { once } from "node:events";
import { spawn } from "node:child_process";
import { test } from "node:test";
import { fileURLToPath } from "node:url";

// Teste de contrato HTTP: Next real + upstream isolado, sem serviços de produção.
test("gateway de autenticação e conversas do FastAPI", { timeout: 45000 }, async t => {
  const id = "01900000-0000-7000-8000-000000000001";
  const citationId = "01900000-0000-7000-8000-000000000002";
  const user = { id, name: "Conta de teste", email: "teste@example.com", role: "USER", is_active: true };
  const conversation = { id, title: "Férias", created_at: "2026-10-29T12:00:00Z", updated_at: "2026-10-29T12:00:00Z" };
  const citation = { id: citationId, citation_number: 1, original_quote: "Trecho de teste." };
  const messages = [];
  const calls = [];
  let guestUsed = 0;
  const fixture = createServer(async (request, response) => {
    let text = "";
    for await (const chunk of request) text += chunk;
    const payload = text ? JSON.parse(text) : null;
    const url = new URL(request.url, "http://fixture");
    calls.push({ method: request.method, path: url.pathname, query: url.search, payload, authorization: request.headers.authorization, anonymousToken: request.headers["x-anonymous-token"] });
    const reply = (data, status = 200) => { response.writeHead(status, { "Content-Type": "application/json" }); response.end(JSON.stringify(data)); };
    if (url.pathname === "/api/v1/auth/anonymous") return reply({ anonymous_token: "segredo-anonimo", questions_used: guestUsed, questions_limit: 3, expires_at: new Date(Date.now() + 14400000).toISOString() });
    if (["/api/v1/auth/login", "/api/v1/auth/register"].includes(url.pathname)) {
      if (payload.password === "incorreta") return reply({ detail: "Invalid credentials" }, 401);
      if (payload.email === "duplicado@example.com") return reply({ detail: "E-mail já cadastrado." }, 409);
      if (payload.email === "invalido@example.com") return reply({ detail: [{ msg: "invalid" }] }, 422);
      return reply({ access_token: "jwt-apenas-no-cookie", token_type: "bearer", user }, request.url.endsWith("register") ? 201 : 200);
    }
    const guest = request.headers["x-anonymous-token"] === "segredo-anonimo" && !request.headers.authorization;
    if (!guest && request.headers.authorization !== "Bearer jwt-apenas-no-cookie") return reply({ detail: "Sessão inválida" }, 401);
    if (url.pathname === "/api/v1/auth/me") return reply(user);
    if (url.pathname === "/api/v1/conversations") return reply(request.method === "POST" ? conversation : { items: [conversation], total: 1 }, request.method === "POST" ? 201 : 200);
    if (url.pathname === `/api/v1/conversations/${id}`) return reply({ ...conversation, messages });
    if (url.pathname === `/api/v1/conversations/${id}/messages`) {
      if (guest && guestUsed >= 3) return reply({ detail: "Entre para continuar a conversa." }, 429);
      if (guest) guestUsed++;
      const make = (role, content, status = "COMPLETED", citations = []) => ({ id: `${id}-${messages.length}`, role, content, status, citations, created_at: conversation.created_at });
      messages.push(make("USER", payload.content));
      if (payload.content === "falhar") {
        messages.push(make("ASSISTANT", "Falha ao gerar resposta.", "FAILED"));
        return reply({ detail: "Provider error: segredo-interno" }, 502);
      }
      const answer = make("ASSISTANT", "Resposta de teste [1].", "COMPLETED", [citation]);
      messages.push(answer); return reply(answer, 201);
    }
    if (url.pathname === `/api/v1/citations/${citationId}`) return reply({ ...citation, chunk: { official_url: "https://www.planalto.gov.br/", article: "Art. 1", section: null, paragraph: null }, source: { name: "Planalto", short_name: "PR", base_url: "https://www.planalto.gov.br/" } });
    return reply({ detail: "Não encontrado" }, 404);
  });
  fixture.listen(0, "127.0.0.1"); await once(fixture, "listening");
  const reserve = createServer(); reserve.listen(0, "127.0.0.1"); await once(reserve, "listening");
  const port = reserve.address().port;
  await new Promise(resolve => reserve.close(resolve));
  const origin = `http://127.0.0.1:${port}`;
  let logs = "";
  const server = spawn(process.execPath, ["node_modules/next/dist/bin/next", "start", "--hostname", "127.0.0.1", "--port", String(port)], {
    cwd: fileURLToPath(new URL("../", import.meta.url)),
    env: { ...process.env, NODE_ENV: "production", BACKEND_API_URL: `http://127.0.0.1:${fixture.address().port}` },
    windowsHide: true, stdio: ["ignore", "pipe", "pipe"],
  });
  server.stdout.on("data", chunk => { logs += chunk; }); server.stderr.on("data", chunk => { logs += chunk; });
  t.after(async () => {
    if (server.exitCode === null) { server.kill(); await once(server, "exit"); }
    fixture.closeAllConnections(); await new Promise(resolve => fixture.close(resolve));
  });
  const call = (path, { method = "GET", body, cookie, requestOrigin = origin } = {}) => fetch(`${origin}/api/backend/${path}`, {
    method, headers: { "Content-Type": "application/json", Origin: requestOrigin, ...(cookie ? { Cookie: cookie } : {}) },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });
  let ready = false;
  for (let attempt = 0; attempt < 150; attempt++) {
    if (server.exitCode !== null) throw new Error(logs);
    try { await call("auth/session"); ready = true; break; } catch { await new Promise(resolve => setTimeout(resolve, 100)); }
  }
  assert.ok(ready, logs);

  await t.test("landing oferece Entrar e as rotas não impõem formulário de login", async () => {
    for (const path of ["/", "/chat"]) {
      const response = await fetch(`${origin}${path}`);
      assert.equal(response.status, 200);
      const html = await response.text();
      if (path === "/") assert.match(html, /Entrar/);
      assert.ok(!html.includes('name="password"'), "O login só monta ao abrir o diálogo");
    }
  });

  await t.test("bloqueia acesso anônimo e rotas fora do contrato", async () => {
    assert.equal((await call("conversations")).status, 401);
    assert.equal((await call("documents", { method: "POST", body: {} })).status, 404);
    assert.equal(calls.length, 0);
  });
  await t.test("bloqueia login de outra origem", async () => {
    assert.equal((await call("auth/login", { method: "POST", body: {}, requestOrigin: "https://outro.example.com" })).status, 403);
    assert.equal(calls.length, 0);
  });
  let cookie;
  let guestCookie;
  await t.test("sessão anônima permite três perguntas e mantém o token privado", async () => {
    const started = await call("auth/anonymous", { method: "POST", body: {} });
    assert.equal(started.status, 200);
    const session = await started.json();
    assert.equal(session.questions_limit, 3); assert.equal(session.anonymous_token, undefined);
    const header = started.headers.get("set-cookie");
    assert.ok(header.includes("HttpOnly")); guestCookie = header.split(";")[0];
    assert.equal((await call("conversations", { method: "POST", cookie: guestCookie, body: { title: "Sem cadastro" } })).status, 201);
    for (let index = 0; index < 3; index++) {
      const response = await call(`conversations/${id}/messages`, { method: "POST", cookie: guestCookie, body: { content: "Pergunta sem conta" } });
      assert.equal(response.status, 201);
    }
    assert.equal(calls.at(-1).anonymousToken, "segredo-anonimo");
    assert.equal((await call(`conversations/${id}/messages`, { method: "POST", cookie: guestCookie, body: { content: "Quarta" } })).status, 429);
    assert.equal((await (await call("auth/anonymous", { method: "POST", cookie: guestCookie, body: {} })).json()).questions_used, 3);
    messages.length = 0;
  });
  await t.test("cadastro e login retornam perfil sem expor JWT", async () => {
    const registered = await call("auth/register", { method: "POST", body: { name: user.name, email: user.email, password: "senha-teste" } });
    assert.equal(registered.status, 201); assert.deepEqual(await registered.json(), user);
    const response = await call("auth/login", { method: "POST", cookie: guestCookie, body: { email: user.email, password: "senha-teste" } });
    assert.deepEqual(await response.json(), user);
    const header = response.headers.get("set-cookie");
    for (const attribute of ["HttpOnly", "Secure", "SameSite=lax", "Path=/"]) assert.ok(header.includes(attribute), header);
    assert.equal(response.headers.get("cache-control"), "no-store");
    cookie = header.split(";")[0];
    assert.equal(calls.at(-1).authorization, undefined);
    assert.equal(calls.at(-1).anonymousToken, "segredo-anonimo", "Login encaminha a sessão para migrar as conversas");
    assert.match(response.headers.get("set-cookie"), /direito_anonymous=;/);
  });
  await t.test("apresenta erros de credenciais, cadastro e validação", async () => {
    assert.equal((await call("auth/login", { method: "POST", body: { password: "incorreta" } })).status, 401);
    assert.equal((await call("auth/register", { method: "POST", body: { email: "duplicado@example.com" } })).status, 409);
    const invalid = await call("auth/register", { method: "POST", body: { email: "invalido@example.com" } });
    assert.equal(invalid.status, 422); assert.equal(typeof (await invalid.json()).detail, "string");
  });
  await t.test("retoma sessão, pagina histórico e preserva payloads", async () => {
    assert.deepEqual(await (await call("auth/session", { cookie })).json(), user);
    assert.equal(calls.at(-1).authorization, "Bearer jwt-apenas-no-cookie");
    assert.equal((await call("conversations?offset=20&limit=10&ignorado=1", { cookie })).status, 200);
    assert.equal(calls.at(-1).query, "?offset=20&limit=10");
    const created = await call("conversations", { method: "POST", cookie, body: { title: "Férias" } });
    assert.equal(created.status, 201); assert.equal((await created.json()).id, id);
    const answer = await call(`conversations/${id}/messages`, { method: "POST", cookie, body: { content: "Como funcionam as férias?" } });
    assert.equal(answer.status, 201); assert.deepEqual((await answer.json()).citations, [citation]);
    assert.deepEqual(calls.at(-1).payload, { content: "Como funcionam as férias?" });
    const detail = await (await call(`conversations/${id}`, { cookie })).json();
    assert.equal(detail.messages.length, 2); assert.equal(detail.messages[0].role, "USER");
    const source = await (await call(`citations/${citationId}`, { cookie })).json();
    assert.equal(source.chunk.official_url, "https://www.planalto.gov.br/");
  });
  await t.test("preserva falhas do chat e não repete o POST", async () => {
    const failed = await call(`conversations/${id}/messages`, { method: "POST", cookie, body: { content: "falhar" } });
    assert.equal(failed.status, 502); assert.ok(!(await failed.text()).includes("segredo-interno"));
    const detail = await (await call(`conversations/${id}`, { cookie })).json();
    assert.equal(detail.messages.at(-1).status, "FAILED");
    assert.equal(calls.filter(item => item.payload?.content === "falhar").length, 1);
  });
  await t.test("expiração e logout removem a sessão", async () => {
    const expired = await call("conversations", { cookie: "direito_session=expirado" });
    assert.equal(expired.status, 401); assert.match(expired.headers.get("set-cookie"), /direito_session=;/);
    assert.equal((await call("auth/session", { method: "DELETE", cookie, requestOrigin: "https://outro.example.com" })).status, 403);
    const loggedOut = await call("auth/session", { method: "DELETE", cookie });
    assert.equal(loggedOut.status, 200); assert.match(loggedOut.headers.get("set-cookie"), /direito_session=;/);
  });
  await t.test("backend indisponível retorna erro acionável", async () => {
    fixture.closeAllConnections(); await new Promise(resolve => fixture.close(resolve));
    const response = await call("auth/login", { method: "POST", body: { email: user.email, password: "senha-teste" } });
    assert.equal(response.status, 503); assert.match((await response.json()).detail, /conectar/);
  });
});
