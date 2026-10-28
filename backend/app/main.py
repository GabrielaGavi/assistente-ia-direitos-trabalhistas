"""Entrada ASGI do backend e registro dos routers implementados."""

from fastapi import FastAPI

from app.citations.router import router as citations_router
from app.documents.router import router as documents_router
from app.sources.router import router as sources_router

app = FastAPI(title="Assistente de Direitos Trabalhistas")
app.include_router(citations_router)
app.include_router(sources_router)
app.include_router(documents_router)
