from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Dict
from ..utils.tokens import TokenAnalyzer

router = APIRouter()

class TokenTextRequest(BaseModel):
    text: str = Field(..., description="Raw prompt text to analyze")
    model: str = Field("gpt-5-nano", description="Model for tokenizer/pricing")
    assume_output_tokens: int = Field(200, ge=0, le=8000)

class TokenMessagesRequest(BaseModel):
    messages: List[Dict[str, str]] = Field(..., description="List of {role, content}")
    model: str = Field("gpt-5-nano", description="Model for tokenizer/pricing")
    assume_output_tokens: int = Field(200, ge=0, le=8000)

@router.post("/text", summary="Count tokens & estimate cost for raw text")
def tokens_for_text(req: TokenTextRequest):
    ta = TokenAnalyzer(model=req.model)
    rep = ta.report_for_text(req.text, assume_output_tokens=req.assume_output_tokens)
    return {
        "model": rep.model,
        "input_tokens": rep.input_tokens,
        "assumed_output_tokens": rep.assumed_output_tokens,
        "estimated_cost_usd": round(rep.est_cost_usd, 8),
    }

@router.post("/messages", summary="Count tokens & estimate cost for chat messages")
def tokens_for_messages(req: TokenMessagesRequest):
    ta = TokenAnalyzer(model=req.model)
    rep = ta.report_for_messages(req.messages, assume_output_tokens=req.assume_output_tokens)
    return {
        "model": rep.model,
        "input_tokens": rep.input_tokens,
        "assumed_output_tokens": rep.assumed_output_tokens,
        "estimated_cost_usd": round(rep.est_cost_usd, 8),
    }
