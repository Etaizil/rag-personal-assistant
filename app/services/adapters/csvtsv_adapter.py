from __future__ import annotations
from pathlib import Path
from typing import Optional
from .base import IngestAdapter
from .registry import register_adapter


class CsvTsvAdapter(IngestAdapter):
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
        out = "\n".join(rows).strip()
        return out or None


register_adapter("csvtsv", CsvTsvAdapter(), exts=CsvTsvAdapter.exts)
