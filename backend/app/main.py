"""Entrada ASGI do backend e registro dos routers implementados."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.router import router as auth_router
from app.citations.router import router as citations_router
from app.conversations.router import router as conversations_router
from app.documents.router import router as documents_router
from app.sources.router import router as sources_router

app = FastAPI(title="Assistente de Direitos Trabalhistas")

# Origens do frontend em desenvolvimento (Next.js). Em producao, restrinja a
# lista ao dominio real publicado -- "*" com credenciais nao e permitido pela
# especificacao CORS e o navegador rejeitaria silenciosamente.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(citations_router)
app.include_router(sources_router)
app.include_router(documents_router)
app.include_router(conversations_router)


@app.get("/api/v1/health", tags=["health"], summary="Verifica se o backend esta operacional")
async def health() -> dict[str, str]:
    return {"status": "ok"}
