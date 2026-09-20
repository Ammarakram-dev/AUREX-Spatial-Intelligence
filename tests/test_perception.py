"""
AUREX Spatial Intelligence
Perception Architecture Test
"""

import sys
from pathlib import Path
from uuid import uuid4

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from core.engine import AUREXEngine
from core.perception.entities import VisualFrame
from core.perception.manager import PerceptionManager
from core.perception.simulator import SimulatedPerception


def main() -> None:

    engine = AUREXEngine()
    engine.start()

    manager = PerceptionManager(engine)

    simulator = SimulatedPerception()

    manager.add_module(simulator)

    frame = VisualFrame(
        frame_id=str(uuid4()),
        width=1280,
        height=720,
    )

    events = manager.process(frame)

    print("=" * 64)
    print("AUREX PERCEPTION ENGINE TEST")
    print("=" * 64)

    print()

    print("Registered modules:")
    print(manager.status())

    print()

    print("Generated events:")

    for event in events:
        print(event.to_dict())

    print()

    print("Perception test completed successfully.")

    engine.stop()


if __name__ == "__main__":
    main()