from __future__ import annotations
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional
from .base import IngestAdapter
from .registry import register_adapter


class HtmlAdapter(IngestAdapter):
    exts = {".html", ".htm"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.exts

    def load_text(self, path: Path) -> Optional[str]:
        soup = BeautifulSoup(
            path.read_text(encoding="utf-8", errors="ignore"), "html.parser"
        )
        for s in soup(["script", "style"]):
            s.extract()
        text = soup.get_text(separator="\n").strip()
        return text or None


register_adapter("html", HtmlAdapter(), exts=HtmlAdapter.exts)
