from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Protocol


class IngestAdapter(Protocol):
    def can_handle(self, path: Path) -> bool: ...
    def load_text(self, path: Path) -> Optional[str]: ...


@dataclass(frozen=True)
class RegisteredAdapter:
    name: str
    impl: IngestAdapter
