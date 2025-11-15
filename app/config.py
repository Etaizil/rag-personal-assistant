from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-5-nano")
    openai_embed_model: str = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    embeddings_backend: str = os.getenv(
        "EMBEDDINGS_BACKEND", "local"
    ).lower()  # "openai" or "local"
    rag_top_k: int = int(os.getenv("RAG_TOP_K", "4"))
    chroma_dir: str = os.getenv("CHROMA_DIR", ".chroma")
    max_input_tokens: int = int(os.getenv("MAX_INPUT_TOKENS", "5000"))
    max_output_tokens: int = int(os.getenv("MAX_OUTPUT_TOKENS", "200"))

    ingest_max_chars: int = int(os.getenv("INGEST_MAX_CHARS", "8000"))
    ingest_overlap: int = int(os.getenv("INGEST_OVERLAP", "300"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "128"))

    debug: bool = os.getenv("DEBUG", "False").strip().lower() in (
        "1",
        "true",
        "yes",
        "y",
        "on",
    )
    system_prompt: str = os.getenv(
        "SYSTEM_PROMPT",
        "You are a concise, helpful AI assistant. Use the provided context only. If the context does not contain the answer, say 'Not found in context.' Keep answers brief.",
    )


settings = Settings()
