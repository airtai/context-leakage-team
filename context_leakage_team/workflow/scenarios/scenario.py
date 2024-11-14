from typing import Any, Protocol

from fastagency import UI


class Scenario(Protocol):
    def __init__(self):
        ...

    @classmethod
    def run(cls, ui: UI, params: dict[str, Any]) -> str:
        ...

    @classmethod
    def report(cls, ui: UI, params: dict[str, Any]) -> None:
        ...