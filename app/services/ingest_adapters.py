from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Protocol

from pypdf import PdfReader
from bs4 import BeautifulSoup


# ---------- Adapter Protocol ----------


class IngestAdapter(Protocol):
    def can_handle(self, path: Path) -> bool: ...
    def load_text(self, path: Path) -> Optional[str]: ...


@dataclass(frozen=True)
class RegisteredAdapter:
    name: str
    impl: IngestAdapter


_REGISTRY: list[RegisteredAdapter] = []


def register_adapter(name: str, impl: IngestAdapter) -> None:
    _REGISTRY.append(RegisteredAdapter(name, impl))


def all_adapters() -> Iterable[RegisteredAdapter]:
    return list(_REGISTRY)


def pick_adapter(path: Path) -> Optional[RegisteredAdapter]:
    for a in _REGISTRY:
        if a.impl.can_handle(path):
            return a
    return None


# ---------- Built-in adapters ----------


class TextAdapter:
    exts = {".txt", ".md", ".markdown"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.exts

    def load_text(self, path: Path) -> Optional[str]:
        return path.read_text(encoding="utf-8", errors="ignore")


class PdfAdapter:
    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def load_text(self, path: Path) -> Optional[str]:
        try:
            reader = PdfReader(str(path))
            text = []
            for page in reader.pages:
                t = page.extract_text() or ""
                text.append(t)
            return "\n".join(text).strip() or None
        except Exception:
            return None


class HtmlAdapter:
    exts = {".html", ".htm"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.exts

    def load_text(self, path: Path) -> Optional[str]:
        soup = BeautifulSoup(
            path.read_text(encoding="utf-8", errors="ignore"), "html.parser"
        )
        # Simple readable text (no scripts/styles)
        for s in soup(["script", "style"]):
            s.extract()
        text = soup.get_text(separator="\n")
        return text.strip() or None


class CsvTsvAdapter:
    exts = {".csv", ".tsv"}

    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() in self.exts

    def load_text(self, path: Path) -> Optional[str]:
        import csv

        delim = "\t" if path.suffix.lower() == ".tsv" else ","
        rows = []
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter=delim)
            for row in reader:
                rows.append(" | ".join(row))
        return "\n".join(rows).strip() or None


class JsonAdapter:
    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".json"

    def _flatten(self, obj) -> list[str]:
        out = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                out.append(str(k))
                out.extend(self._flatten(v))
        elif isinstance(obj, list):
            for v in obj:
                out.extend(self._flatten(v))
        else:
            if obj is not None:
                out.append(str(obj))
        return out

    def load_text(self, path: Path) -> Optional[str]:
        import json

        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return None
        pieces = self._flatten(data)
        text = "\n".join(pieces)
        return text.strip() or None


# Register defaults at import time
register_adapter("text", TextAdapter())
register_adapter("pdf", PdfAdapter())
register_adapter("html", HtmlAdapter())
register_adapter("csvtsv", CsvTsvAdapter())
register_adapter("json", JsonAdapter())
