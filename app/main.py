from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers.chat import router as chat_router
from .routers.tools import router as tools_router

app = FastAPI(title="RAG Personal Assistant API")
app.include_router(chat_router, prefix="/chat", tags=["chat"])
app.include_router(tools_router, prefix="/tools/tokens", tags=["tools"])

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"ok": True, "msg": "RAG Assistant running. See /docs"}


app.include_router(chat_router, prefix="", tags=["chat"])
