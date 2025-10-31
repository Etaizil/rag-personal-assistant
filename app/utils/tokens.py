from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict
import tiktoken

PRICE_PER_MILLION = {
    # default fallback (used when model key is missing)
    "__default__": {"in": 0.05, "out": 0.4},
    # GPT-5 family (standard prices per 1M tokens)
    "gpt-5": {"in": 1.25, "out": 10.0},
    "gpt-5-mini": {"in": 0.25, "out": 2.0},
    "gpt-5-nano": {"in": 0.05, "out": 0.4},
    "gpt-5-chat-latest": {"in": 1.25, "out": 10.0},
    "gpt-5-codex": {"in": 1.25, "out": 10.0},
    "gpt-5-pro": {"in": 15.0, "out": 120.0},
    # GPT-4.1 family
    "gpt-4.1": {"in": 2.0, "out": 8.0},
    "gpt-4.1-mini": {"in": 0.4, "out": 1.6},
    "gpt-4.1-nano": {"in": 0.1, "out": 0.4},
    # GPT-4o family
    "gpt-4o": {"in": 2.5, "out": 10.0},
    "gpt-4o-2024-05-13": {"in": 5.0, "out": 15.0},
}

TOKENIZER_BY_MODEL = {
    "gpt-4o-mini": "cl100k_base",
    "gpt-3.5-turbo": "cl100k_base",
}


@dataclass
class TokenReport:
    model: str
    input_tokens: int
    assumed_output_tokens: int
    est_cost_usd: float


class TokenAnalyzer:
    def __init__(self, model: str = "gpt-5-nano"):
        self.model = model
        tokenizer_name = TOKENIZER_BY_MODEL.get(model, "cl100k_base")
        self._enc = tiktoken.get_encoding(tokenizer_name)

    def count_text(self, text: str) -> int:
        return len(self._enc.encode(text or ""))

    def count_messages(self, messages: List[Dict[str, str]]) -> int:
        content = "".join(m.get("content", "") for m in messages or [])
        return self.count_text(content)

    def truncate_text(self, text: str, max_tokens: int) -> str:
        toks = self._enc.encode(text or "")
        if len(toks) <= max_tokens:
            return text
        return self._enc.decode(toks[:max_tokens])

    def estimate_cost_usd(self, input_tokens: int, output_tokens: int) -> float:
        price = PRICE_PER_MILLION.get(self.model, PRICE_PER_MILLION["__default__"])
        return (input_tokens / 1_000_000.0) * price["in"] + (
            output_tokens / 1_000_000.0
        ) * price["out"]

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
