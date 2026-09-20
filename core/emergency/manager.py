"""
AUREX Spatial Intelligence
Emergency Intelligence Manager
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable


class EmergencyLevel(str, Enum):
    NONE = "NONE"
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class EmergencyAlert:
    alert_type: str
    level: EmergencyLevel
    message: str
    confidence: float
    timestamp: str
    source: str
    acknowledged: bool = False

    def acknowledge(self) -> None:
        self.acknowledged = True

    def to_dict(self) -> dict:
        return {
            "alert_type": self.alert_type,
            "level": self.level.value,
            "message": self.message,
            "confidence": self.confidence,
            "timestamp": self.timestamp,
            "source": self.source,
            "acknowledged": self.acknowledged,
        }


class AUREXEmergencyManager:
    """
    Central emergency intelligence layer.

    Converts safety/security events into structured
    emergency alerts and dispatches configured handlers.
    """

    def __init__(self) -> None:
        self.alerts: list[EmergencyAlert] = []
        self.handlers: list[
            Callable[[EmergencyAlert], None]
        ] = []

    def register_handler(
        self,
        handler: Callable[[EmergencyAlert], None],
    ) -> None:
        if handler not in self.handlers:
            self.handlers.append(handler)

    def create_alert(
        self,
        alert_type: str,
        level: EmergencyLevel,
        message: str,
        confidence: float,
        source: str,
    ) -> EmergencyAlert:

        alert = EmergencyAlert(
            alert_type=alert_type,
            level=level,
            message=message,
            confidence=max(
                0.0,
                min(1.0, confidence),
            ),
            timestamp=datetime.now(
                timezone.utc
            ).isoformat(),
            source=source,
        )

        self.alerts.append(alert)

        self._dispatch(alert)

        return alert

    def handle_fall(
        self,
        confidence: float,
        person_id: int | None = None,
    ) -> EmergencyAlert:

        person_text = (
            f"Person {person_id}"
            if person_id is not None
            else "A person"
        )

        return self.create_alert(
            alert_type="FALL_DETECTED",
            level=EmergencyLevel.CRITICAL,
            message=(
                f"{person_text} may have experienced "
                f"a fall."
            ),
            confidence=confidence,
            source="FallGuard",
        )

    def acknowledge_alert(
        self,
        alert_index: int,
    ) -> bool:

        if not (
            0 <= alert_index < len(self.alerts)
        ):
            return False

        self.alerts[alert_index].acknowledge()
        return True

    def active_alerts(
        self,
    ) -> list[EmergencyAlert]:

        return [
            alert
            for alert in self.alerts
            if not alert.acknowledged
        ]

    def latest_alert(
        self,
    ) -> EmergencyAlert | None:

        if not self.alerts:
            return None

        return self.alerts[-1]

    def _dispatch(
        self,
        alert: EmergencyAlert,
    ) -> None:

        for handler in list(self.handlers):
            try:
                handler(alert)
            except Exception:
                # One failed handler must not stop
                # the emergency pipeline.
                continue

    def status(self) -> dict:
        return {
            "total_alerts": len(self.alerts),
            "active_alerts": len(
                self.active_alerts()
            ),
            "handlers": len(self.handlers),
            "latest_alert": (
                self.latest_alert().to_dict()
                if self.latest_alert()
                else None
            ),
        }