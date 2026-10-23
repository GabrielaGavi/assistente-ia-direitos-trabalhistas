"""Entrada ASGI do backend; demais routers serao integrados na T029."""

from fastapi import FastAPI

from app.citations.router import router as citations_router

app = FastAPI(title="Assistente de Direitos Trabalhistas")
app.include_router(citations_router)
