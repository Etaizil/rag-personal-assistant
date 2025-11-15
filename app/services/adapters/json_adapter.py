from __future__ import annotations
from pathlib import Path
from typing import Optional, List, Any
from .base import IngestAdapter
from .registry import register_adapter


class JsonAdapter(IngestAdapter):
    def can_handle(self, path: Path) -> bool:
        return path.suffix.lower() == ".json"

    def _flatten(self, obj: Any, out: List[str]) -> None:
        if isinstance(obj, dict):
            for k, v in obj.items():
                out.append(str(k))
                self._flatten(v, out)
        elif isinstance(obj, list):
            for v in obj:
                self._flatten(v, out)
        else:
            if obj is not None:
                out.append(str(obj))

    def load_text(self, path: Path) -> Optional[str]:
        import json

        try:
            data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
        except Exception:
            return None
        buf: List[str] = []
        self._flatten(data, buf)
        out = "\n".join(buf).strip()
        return out or None


register_adapter("json", JsonAdapter(), exts={".json"})
