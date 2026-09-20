"""
AUREX Spatial Intelligence
Perception Manager
"""

from __future__ import annotations

from typing import Any

from ..engine import AUREXEngine
from ..events import AUREXEvent
from .base import PerceptionModule
from .entities import VisualFrame


class PerceptionManager:
    """
    Coordinates all perception modules.

    The manager does not know how individual AI models work.
    It only coordinates their outputs.
    """

    def __init__(
        self,
        engine: AUREXEngine,
    ) -> None:

        self.engine = engine

        self.modules: dict[
            str,
            PerceptionModule,
        ] = {}

    def add_module(
        self,
        module: PerceptionModule,
    ) -> None:
        """Register a perception module."""

        if module.name in self.modules:
            raise ValueError(
                f"Perception module already exists: "
                f"{module.name}"
            )

        self.modules[module.name] = module

    def process(
        self,
        frame: VisualFrame,
    ) -> list[AUREXEvent]:
        """
        Process a frame through every registered module.
        """

        events: list[AUREXEvent] = []

        for module in self.modules.values():

            generated = module.process(frame)

            for event in generated:
                self.engine.emit(event)
                events.append(event)

        return events

    def status(self) -> dict[str, Any]:
        """Return perception system status."""

        return {
            "modules": [
                module.status()
                for module in self.modules.values()
            ],
            "module_count": len(self.modules),
        }