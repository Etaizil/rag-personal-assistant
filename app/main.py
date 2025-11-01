import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.chat import chat_router
from .routers.models import models_router

app = FastAPI(title="RAG Personal Assistant API")
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(models_router, prefix="/models", tags=["models"])

_allowed = os.getenv("ALLOWED_ORIGINS", None)
allow_origins = [o.strip() for o in _allowed.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.get("/")
def root():
    return {"ok": True, "msg": "RAG Assistant running. See /docs"}
