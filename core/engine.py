"""
AUREX Spatial Intelligence
Central Intelligence Engine
"""

from __future__ import annotations

from typing import Any, Callable

from .events import AUREXEvent
from .registry import ModuleRegistry
from .state import WorldState


class AUREXEngine:
    """
    Central runtime for AUREX Spatial Intelligence.

    Responsibilities:

    - maintain world state
    - register capabilities
    - receive events
    - dispatch events
    - expose system status
    """

    def __init__(self) -> None:
        self.state = WorldState()
        self.registry = ModuleRegistry()

        self._subscribers: dict[
            str, list[Callable[[AUREXEvent], None]]
        ] = {}

        self.running = False

    def start(self) -> None:
        """Start the AUREX engine."""

        self.running = True
        self.state.update_timestamp()

    def stop(self) -> None:
        """Stop the AUREX engine."""

        self.running = False
        self.state.update_timestamp()

    def subscribe(
        self,
        event_type: str,
        handler: Callable[[AUREXEvent], None],
    ) -> None:
        """Subscribe a handler to an event type."""

        self._subscribers.setdefault(
            event_type, []
        ).append(handler)

    def emit(self, event: AUREXEvent) -> None:
        """
        Process an incoming event and notify subscribers.
        """

        if not self.running:
            raise RuntimeError(
                "AUREX Engine is not running."
            )

        handlers = self._subscribers.get(
            event.event_type,
            [],
        )

        for handler in handlers:
            handler(event)

        self.state.update_timestamp()

    def register_module(
        self,
        name: str,
        version: str,
        description: str,
        handler: Callable[..., Any],
    ) -> None:
        """Register a capability."""

        self.registry.register(
            name=name,
            version=version,
            description=description,
            handler=handler,
        )

    def status(self) -> dict[str, Any]:
        """Return the current engine status."""

        return {
            "system": "AUREX Spatial Intelligence",
            "engine": "AUREX Core",
            "running": self.running,
            "registered_modules": self.registry.count(),
            "active_alerts": len(self.state.alerts),
            "people_tracked": len(self.state.people),
            "objects_tracked": len(self.state.objects),
            "timestamp": self.state.updated_at,
        }