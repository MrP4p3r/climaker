from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Dict

from .exceptions import TokenParserError


__all__ = [
    'ParserResult',
]


@dataclass(frozen=True)
class ParserResult:
    name: str
    args: Optional[Dict[str, Any]] = None
    error: Optional[TokenParserError] = None
    child: ParserResult = None
