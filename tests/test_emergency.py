import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.emergency.manager import (
    AUREXEmergencyManager,
    EmergencyAlert,
    EmergencyLevel,
)


def emergency_handler(
    alert: EmergencyAlert,
) -> None:

    print()
    print("!" * 60)
    print("AUREX EMERGENCY ALERT")
    print("!" * 60)
    print(f"TYPE: {alert.alert_type}")
    print(f"LEVEL: {alert.level.value}")
    print(f"MESSAGE: {alert.message}")
    print(
        f"CONFIDENCE: "
        f"{alert.confidence * 100:.1f}%"
    )
    print(f"SOURCE: {alert.source}")
    print(f"TIME: {alert.timestamp}")
    print("!" * 60)


def main():

    print("=" * 60)
    print("AUREX EMERGENCY INTELLIGENCE TEST")
    print("=" * 60)

    manager = AUREXEmergencyManager()

    manager.register_handler(
        emergency_handler
    )

    alert = manager.handle_fall(
        confidence=0.86,
        person_id=1,
    )

    print()
    print("Alert created:")
    print(alert.to_dict())

    print()
    print("System status:")
    print(manager.status())

    print()
    print("Acknowledging alert...")

    success = manager.acknowledge_alert(0)

    print(
        "Acknowledged:",
        success,
    )

    print()
    print("Active alerts:")
    print(
        len(manager.active_alerts())
    )

    assert alert.level == (
        EmergencyLevel.CRITICAL
    )

    assert alert.alert_type == (
        "FALL_DETECTED"
    )

    assert alert.acknowledged is True

    print()
    print("=" * 60)
    print("EMERGENCY TEST PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()