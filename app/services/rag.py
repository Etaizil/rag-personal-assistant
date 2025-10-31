from .vectorstore import LocalVectorStore
from .ingest import truncate_tokens
from ..config import settings
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
        self.system_prompt = settings.system_prompt

    def build_prompt(self, query: str, docs: list[dict]) -> list[dict]:
        context_blocks = []
        for d in docs:
            block = f"Source: {d.get('source','unknown')}\n---\n{d['text']}"
            context_blocks.append(block)
        context = "\n\n".join(context_blocks)
        user = f"Question: {query}\n\nContext:\n{context}"
        user = truncate_tokens(user, self.max_input_tokens)
        return [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user},
        ]

    def answer(self, query: str):
        docs = self.vs.similarity_search(query, k=self.top_k)
        messages = self.build_prompt(query, docs)
        resp = self.client.chat.completions.create(model=self.model, messages=messages)
        answer = resp.choices[0].message.content
        sources = [d.get("source", "unknown") for d in docs]
        usage = getattr(resp, "usage", None)
        return answer, sources, usage
