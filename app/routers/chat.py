from fastapi import APIRouter
from pydantic import BaseModel
from ..services.rag import RAGPipeline

router = APIRouter()
rag = RAGPipeline()  # uses env-configured defaults


class ChatRequest(BaseModel):
    query: str


@router.post("/", summary="Ask the assistant")
def chat(req: ChatRequest):
    answer, sources, usage = rag.answer(req.query)
    return {"answer": answer, "sources": sources, "usage": usage}
