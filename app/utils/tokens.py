from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import tiktoken
from .model_registry import ModelManager

MESSAGE_OVERHEAD = 6  # rough per-message overhead


@dataclass
class TokenReport:
    model: str
    input_tokens: int
    assumed_output_tokens: int
    est_cost_usd: float


class TokenAnalyzer:
    def __init__(self, model: str = "gpt-5-nano"):
        self.model = model
        tokenizer_name = "cl100k_base"
        self._enc = tiktoken.get_encoding(tokenizer_name)

    def count_text(self, text: str) -> int:
        return len(self._enc.encode(text or ""))

    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        total = 0
        for m in messages or []:
            total += len(self._enc.encode(m.get("content", "") or ""))
            total += MESSAGE_OVERHEAD
        return total

    def truncate_text(self, text: str, max_tokens: int) -> str:
        toks = self._enc.encode(text or "")
        if len(toks) <= max_tokens:
            return text
        return self._enc.decode(toks[:max_tokens])

    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        return ModelManager.estimate_cost_usd(self.model, input_tokens, output_tokens)

    def report_for_text(
        self, text: str, assume_output_tokens: int = 200
    ) -> TokenReport:
        itoks = self.count_text(text)
        cost = self.estimate_cost_usd(itoks, assume_output_tokens)
        return TokenReport(self.model, itoks, assume_output_tokens, cost)

    def report_for_messages(
        self, messages: List[Dict[str, str]], assume_output_tokens: int = 200
    ) -> TokenReport:
        itoks = self.count_messages(messages)
        cost = self.estimate_cost_usd(itoks, assume_output_tokens)
        return TokenReport(self.model, itoks, assume_output_tokens, cost)
