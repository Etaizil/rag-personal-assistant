from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple

from ..config import settings
from .vectorstore import LocalVectorStore
from .adapters import pick_adapter  # from __init__.py


@dataclass(frozen=True)
class ChunkConfig:
    max_chars: int | None = 8000
    overlap: int = 300
    batch_size: int = 128


class TextChunker:
    def __init__(self, cfg: ChunkConfig):
        self.cfg = cfg

    def chunk(self, text: str) -> Iterable[str]:
        if not text:
            return
        if self.cfg.max_chars is None or len(text) <= self.cfg.max_chars:
            yield text
            return
        n = len(text)
        k = self.cfg.max_chars
        o = max(0, min(self.cfg.overlap, k - 1))
        start = 0
        while start < n:
            end = min(start + k, n)
            yield text[start:end]
            if end == n:
                break
            start = end - o


class IngestService:
    def __init__(self, vs: LocalVectorStore, chunker: TextChunker):
        self.vs = vs
        self.chunker = chunker

    def _to_records(
        self, path: Path, raw: str
    ) -> Tuple[List[str], List[str], List[dict]]:
        docs: List[str] = []
        ids: List[str] = []
        metas: List[dict] = []
        adapter = pick_adapter(path)
        adapter_name = adapter.name if adapter else "unknown"
        for i, chunk in enumerate(self.chunker.chunk(raw)):
            docs.append(chunk)
            ids.append(f"{path.as_posix()}#{i}")
            metas.append(
                {"source": path.as_posix(), "chunk": i, "adapter": adapter_name}
            )
        return docs, ids, metas

    def ingest_file(self, path: Path) -> int:
        if not path.is_file():
            return 0
        ra = pick_adapter(path)
        if not ra:
            return 0
        text = ra.impl.load_text(path)
        if not text:
            return 0
        docs, ids, metas = self._to_records(path, text)
        if not docs:
            return 0
        b = max(1, settings.getint("BATCH_SIZE", default=128))
        for i in range(0, len(docs), b):
            self.vs.add_texts(docs[i : i + b], ids[i : i + b], metas[i : i + b])
        return len(docs)

    def ingest_dir(self, root: Path) -> int:
        assert root.exists() and root.is_dir()
        total = 0
        for p in root.rglob("*"):
            total += self.ingest_file(p)
        return total


def ingest_dir(dir_path: str) -> int:
    root = Path(dir_path)
    vs = LocalVectorStore(
        settings.chroma_dir, settings.openai_embed_model, settings.openai_api_key
    )
    maxc = settings.getint("INGEST_MAX_CHARS", default=8000)
    maxc = None if maxc is not None and maxc <= 0 else maxc
    cfg = ChunkConfig(
        max_chars=maxc,
        overlap=settings.getint("INGEST_OVERLAP", default=300),
        batch_size=settings.getint("BATCH_SIZE", default=128),
    )
    service = IngestService(vs, TextChunker(cfg))
    return service.ingest_dir(root)
