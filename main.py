"""
AUREX Spatial Intelligence
System Entry Point
"""

from core.engine import AUREXEngine
from core.events import create_event


def main() -> None:
    engine = AUREXEngine()

    engine.start()

    print("=" * 64)
    print("AUREX SPATIAL INTELLIGENCE")
    print("AUREX CORE v0.1")
    print("=" * 64)

    print()

    print("System Status:")

    status = engine.status()

    for key, value in status.items():
        print(f"  {key}: {value}")

    print()

    perception_event = create_event(
        event_type="system.perception.ready",
        source="aurex.bootstrap",
        data={
            "message": "Perception layer initialized."
        },
    )

    engine.emit(perception_event)

    print("Initial event processed successfully.")
    print()

    engine.stop()

    print("AUREX Core shutdown complete.")


if __name__ == "__main__":
    main()