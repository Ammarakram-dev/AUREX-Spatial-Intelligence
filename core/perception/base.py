"""
AUREX Spatial Intelligence
Base Perception Module
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..events import AUREXEvent
from .entities import VisualFrame


class PerceptionModule(ABC):
    """
    Base interface for every AUREX perception component.

    Examples:

    - camera perception
    - person detection
    - object detection
    - gesture recognition
    - face analysis
    - eye tracking
    """

    name: str = "unknown"
    version: str = "0.1.0"

    @abstractmethod
    def process(
        self,
        frame: VisualFrame,
    ) -> list[AUREXEvent]:
        """
        Process one visual frame and generate events.
        """

        raise NotImplementedError

    def status(self) -> dict[str, Any]:
        """Return module information."""

        return {
            "name": self.name,
            "version": self.version,
            "type": self.__class__.__name__,
        }