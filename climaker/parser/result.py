from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Mapping

from .exceptions import TokenParsingError


__all__ = [
    'TokenParsingResult',
]


@dataclass(frozen=True)
class TokenParsingResult:
    name: str
    args: Optional[Mapping[str, Any]] = None
    error: Optional[TokenParsingError] = None
    child: Optional[TokenParsingResult] = None
