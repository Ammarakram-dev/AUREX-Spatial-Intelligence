"""
AUREX Spatial Intelligence
Module Registry

Provides a controlled way for AUREX capabilities to
register themselves with the central engine.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class ModuleInfo:
    name: str
    version: str
    description: str
    handler: Callable[..., Any]


class ModuleRegistry:

    def __init__(self) -> None:
        self._modules: dict[str, ModuleInfo] = {}

    def register(
        self,
        name: str,
        version: str,
        description: str,
        handler: Callable[..., Any],
    ) -> None:
        """Register an AUREX module."""

        if name in self._modules:
            raise ValueError(
                f"Module already registered: {name}"
            )

        self._modules[name] = ModuleInfo(
            name=name,
            version=version,
            description=description,
            handler=handler,
        )

    def get(self, name: str) -> ModuleInfo | None:
        """Retrieve a registered module."""

        return self._modules.get(name)

    def list_modules(self) -> list[ModuleInfo]:
        """Return all registered modules."""

        return list(self._modules.values())

    def count(self) -> int:
        """Return the number of registered modules."""

        return len(self._modules)