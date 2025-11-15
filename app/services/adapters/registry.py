from __future__ import annotations
from pathlib import Path
from typing import Dict, List, Optional, Iterable
from .base import RegisteredAdapter, IngestAdapter

_REGISTRY: List[RegisteredAdapter] = []
_EXT_INDEX: Dict[str, RegisteredAdapter] = {}  # O(1) lookup
_PREDICATE: List[RegisteredAdapter] = []


def register_adapter(
    name: str,
    impl: IngestAdapter,
    exts: Iterable[str] | None = None,
    predicate_only: bool = False,
) -> None:
    ra = RegisteredAdapter(name=name, impl=impl)
    _REGISTRY.append(ra)
    if predicate_only:
        _PREDICATE.append(ra)
        return
    if exts:
        for e in exts:
            _EXT_INDEX[e.lower()] = ra
    else:
        _PREDICATE.append(ra)


def all_adapters() -> List[RegisteredAdapter]:
    return list(_REGISTRY)


def pick_adapter(path: Path) -> Optional[RegisteredAdapter]:
    ext = path.suffix.lower()
    if ext in _EXT_INDEX:
        return _EXT_INDEX[ext]
    for ra in _PREDICATE:
        if ra.impl.can_handle(path):
            return ra
    return None
