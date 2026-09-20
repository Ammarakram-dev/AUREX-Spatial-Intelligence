"""
AUREX Spatial Intelligence
World State

Maintains the current internal representation of
people, objects, environment, security state,
active alerts, and system metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class WorldState:
    """
    Shared state representing AUREX's current understanding
    of the environment.
    """

    people: dict[str, dict[str, Any]] = field(default_factory=dict)

    objects: dict[str, dict[str, Any]] = field(default_factory=dict)

    environment: dict[str, Any] = field(default_factory=dict)

    security: dict[str, Any] = field(
        default_factory=lambda: {
            "mode": "normal",
            "authorized_users": [],
            "active_threats": [],
        }
    )

    alerts: list[dict[str, Any]] = field(default_factory=list)

    active_intents: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(default_factory=dict)

    updated_at: str = field(
        default_factory=lambda: datetime.now(
            timezone.utc
        ).isoformat()
    )

    def update_timestamp(self) -> None:
        """Update the state timestamp."""

        self.updated_at = datetime.now(
            timezone.utc
        ).isoformat()

    def snapshot(self) -> dict[str, Any]:
        """Return a serializable snapshot of current state."""

        return {
            "people": self.people.copy(),
            "objects": self.objects.copy(),
            "environment": self.environment.copy(),
            "security": self.security.copy(),
            "alerts": list(self.alerts),
            "active_intents": list(self.active_intents),
            "metadata": self.metadata.copy(),
            "updated_at": self.updated_at,
        }