from fastapi import APIRouter, Query
from pydantic import BaseModel
from ..services.rag import RAGPipeline
from ..config import settings

chat_router = APIRouter()
rag = RAGPipeline()  # uses env-configured defaults


class ChatRequest(BaseModel):
    query: str


@chat_router.post("/", summary="Ask the assistant")
def chat(req: ChatRequest, debug: bool = Query(settings.debug)):
    answer, sources, usage, ctx_and_diag = rag.answer(req.query, debug=debug)
    context, diag = ctx_and_diag
    payload = {"answer": answer, "sources": sources, "usage": usage}
    if debug:
        payload["context_preview"] = context[:600]
        payload["diagnostics"] = diag
    return payload
