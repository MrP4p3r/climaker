from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Mapping


__all__ = [
    'ArgTree',
]


@dataclass(frozen=True)
class ArgTree:
    """
    Represents raw parsing result.

    :ivar name: Name of a tree must be the same as normalized (sub)command name.
    :ivar args: Mapping with parsed arguments.
    :ivar child: Child tree. Used for subcommands.

    """

    name: str
    args: Mapping[str, Any]
    child: Optional[ArgTree] = None
