from __future__ import annotations
from pathlib import Path
from pypdf import PdfReader
from typing import Optional
from .base import IngestAdapter
from .registry import register_adapter


class PdfAdapter(IngestAdapter):
    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def load_text(self, path: Path) -> Optional[str]:
        try:
            reader = PdfReader(str(path))
            text = []
            for page in reader.pages:
                t = page.extract_text() or ""
                text.append(t)
            out = "\n".join(text).strip()
            return out or None
        except Exception:
            return None


register_adapter("pdf", PdfAdapter(), exts={".pdf"})
