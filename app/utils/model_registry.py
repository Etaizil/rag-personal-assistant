from dataclasses import dataclass
from typing import Dict, Optional, List


@dataclass(frozen=True)
class ModelInfo:
    name: str
    family: str
    uses_completion_cap: bool  # True => use max_completion_tokens; else max_tokens
    price_in: float  # USD per 1M input tokens
    price_out: float  # USD per 1M output tokens
    cached_price_in: Optional[float] = None
    context_window: Optional[int] = None


# Central registry (keys are prefixes; first match wins)
_MODEL_REGISTRY: Dict[str, ModelInfo] = {
    # GPT-5 family
    "gpt-5-pro": ModelInfo("gpt-5-pro", "gpt-5", True, 15.00, 120.00),
    "gpt-5-chat-latest": ModelInfo(
        "gpt-5-chat-latest", "gpt-5", True, 1.25, 10.00, 0.125
    ),
    "gpt-5-codex": ModelInfo("gpt-5-codex", "gpt-5", True, 1.25, 10.00, 0.125),
    "gpt-5-mini": ModelInfo("gpt-5-mini", "gpt-5", True, 0.25, 2.00, 0.025),
    "gpt-5-nano": ModelInfo("gpt-5-nano", "gpt-5", True, 0.05, 0.40, 0.005),
    "gpt-5": ModelInfo("gpt-5", "gpt-5", True, 1.25, 10.00, 0.125),
    # GPT-4 / 4o family
    "gpt-4.1-mini": ModelInfo("gpt-4.1-mini", "gpt-4.1", True, 0.40, 1.60, 0.10),
    "gpt-4.1-nano": ModelInfo("gpt-4.1-nano", "gpt-4.1", True, 0.10, 0.40, 0.025),
    "gpt-4.1": ModelInfo("gpt-4.1", "gpt-4.1", True, 2.00, 8.00, 0.50),
    "gpt-4o-mini": ModelInfo("gpt-4o-mini", "gpt-4o", True, 0.15, 0.60, 0.075),
    "gpt-4o": ModelInfo("gpt-4o", "gpt-4o", True, 2.50, 10.00, 1.25),
}


class ModelManager:
    """Single source of truth for model metadata/params/cost."""

    @staticmethod
    def list_models() -> List[str]:
        """Stable, human-friendly list to show in UI/CLI."""
        return list(_MODEL_REGISTRY.keys())

    @staticmethod
    def get_model_info(model_name: str) -> ModelInfo:
        for prefix, info in _MODEL_REGISTRY.items():
            if model_name.startswith(prefix):
                return info
        # Default to modern behavior if unknown
        return ModelInfo(model_name, "unknown", True, 0.0, 0.0)

    @staticmethod
    def chat_cap_param(model_name: str, max_output_tokens: int) -> dict:
        """Return the correct cap parameter for OpenAI Chat API."""
        info = ModelManager.get_model_info(model_name)
        key = "max_completion_tokens" if info.uses_completion_cap else "max_tokens"
        return {key: max_output_tokens}

    @staticmethod
    def estimate_cost_usd(
        model_name: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        info = ModelManager.get_model_info(model_name)
        cost_in = (prompt_tokens / 1_000_000) * info.price_in
        cost_out = (completion_tokens / 1_000_000) * info.price_out
        return round(cost_in + cost_out, 6)
