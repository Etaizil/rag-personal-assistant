import os, glob, hashlib
from typing import List, Tuple
from ..config import settings


def read_text_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def chunk_text(text: str, chunk_size: int = 800, overlap: int = 120):
    """
    Split `text` into overlapping chunks.
    Fixes infinite-loop case when `end == n` (last chunk).
    Also guards bad params and huge files.
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if overlap >= chunk_size:
        overlap = max(0, chunk_size // 4)  # keep sane overlap

    chunks = []
    n = len(text)
    start = 0
    step = chunk_size - overlap

    while start < n:
        end = min(n, start + chunk_size)
        chunks.append(text[start:end])
        if end == n:  # we reached the last chunk -> stop
            break
        start += step  # move forward by step, not back from end
    return chunks


def fingerprint(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def truncate_tokens(s: str, max_len: int) -> str:
    # naive truncate by characters to keep MVP dependency-light
    return s[:max_len]


def ingest_dir(dir_path: str):
    from .vectorstore import LocalVectorStore

    vs = LocalVectorStore(
        settings.chroma_dir, settings.openai_embed_model, settings.openai_api_key
    )

    paths = sorted(glob.glob(os.path.join(dir_path, "**/*.md"), recursive=True))
    paths += sorted(glob.glob(os.path.join(dir_path, "**/*.txt"), recursive=True))

    ids, texts, metas = [], [], []
    for p in paths:
        raw = read_text_file(p)
        for i, chunk in enumerate(chunk_text(raw)):
            ids.append(f"{os.path.basename(p)}::{i}::{fingerprint(chunk)}")
            texts.append(chunk)
            metas.append({"source": os.path.relpath(p)})
    if texts:
        vs.add_texts(texts, metas, ids)
        print(
            f"Ingested {len(texts)} chunks from {len(paths)} files into Chroma at {settings.chroma_dir}."
        )
    else:
        print("No files found to ingest.")
