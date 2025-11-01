from .vectorstore import LocalVectorStore
from .ingest import truncate_tokens
from ..config import settings
from ..utils.model_registry import ModelManager
from ..utils.tokens import TokenAnalyzer
from openai import OpenAI


class RAGPipeline:
    def __init__(self):
        self.vs = LocalVectorStore(
            settings.chroma_dir, settings.openai_embed_model, settings.openai_api_key
        )
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.top_k = settings.rag_top_k
        self.max_input_tokens = settings.max_input_tokens
        self.max_output_tokens = settings.max_output_tokens
        self.system_prompt = settings.system_prompt

    def build_prompt(self, query: str, docs: list[dict]):
        context_blocks = [
            f"Source: {d.get('source','unknown')}\n---\n{d['text']}" for d in docs
        ]
        context = "\n\n".join(context_blocks)
        user = f"Question: {query}\n\nContext:\n{context}"
        user = truncate_tokens(user, self.max_input_tokens)
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user},
        ]
        return messages, context

    def answer(self, query: str, debug: bool = False):
        docs = self.vs.similarity_search(query, k=self.top_k)
        messages, context = self.build_prompt(query, docs)

        cap = ModelManager.chat_cap_param(self.model, self.max_output_tokens)
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            **cap,
        )

        # Pre-call token estimate
        pre_est_input_tokens = None
        if debug:
            token_analyzer = TokenAnalyzer(model=self.model)
            pre_est_input_tokens = token_analyzer.count_messages(messages)

        # ---- NEW: diagnostics ----
        choices = list(getattr(resp, "choices", []) or [])
        first = choices[0] if choices else None
        msg = getattr(first, "message", None)
        finish_reason = getattr(first, "finish_reason", None)
        tool_calls = getattr(msg, "tool_calls", None)
        refusal = getattr(msg, "refusal", None)
        raw_content = getattr(msg, "content", None)
        content_str = (raw_content or "").strip()
        diag = None
        if debug:
            diag = {
                "choice_count": len(choices),
                "finish_reason": finish_reason,
                "has_content": bool(content_str),
                "content_len": len(content_str),
                "has_tool_calls": bool(tool_calls),
                "has_refusal": bool(refusal),
                "cap": cap,
            }
        # -------------------------

        answer = content_str
        sources = [d.get("source", "unknown") for d in docs]
        usage = getattr(resp, "usage", None)
        if usage:
            try:
                prompt_toks = int(usage.prompt_tokens)
                completion_toks = int(usage.completion_tokens)
            except Exception:
                prompt_toks = completion_toks = 0
            est_cost = ModelManager.estimate_cost_usd(
                self.model, prompt_toks, completion_toks
            )
            usage = {
                "prompt_tokens": prompt_toks,
                "completion_tokens": completion_toks,
                "total_tokens": int(
                    getattr(usage, "total_tokens", prompt_toks + completion_toks)
                ),
                "estimated_cost_usd": est_cost,
                "model": self.model,
            }
            if debug and pre_est_input_tokens is not None:
                usage["pre_est_input_tokens"] = pre_est_input_tokens
        return answer, sources, usage, (context, diag)
