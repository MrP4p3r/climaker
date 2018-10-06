"""Parser output object"""

from typing import Any, Dict, List


__all__ = ['Action']


class Action(object):

    def __init__(self, command: List[str], params: Dict[str, Any]):
        self.command = command
        self.params = params

    def __repr__(self):
        return f'Action({self.command!r}, {self.params})'
