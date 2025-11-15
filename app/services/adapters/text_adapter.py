from __future__ import annotations
from pathlib import Path
from typing import Optional
from .base import IngestAdapter
from .registry import register_adapter


class TextAdapter(IngestAdapter):
    exts = {".txt", ".md", ".markdown"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.exts

    def load_text(self, path: Path) -> Optional[str]:
        return path.read_text(encoding="utf-8", errors="ignore")


register_adapter("text", TextAdapter(), exts=TextAdapter.exts)
