"""
AUREX Spatial Intelligence
Perception Simulator

Used for development and testing before real sensors
are connected.
"""

from __future__ import annotations

from uuid import uuid4

from ..events import create_event
from .base import PerceptionModule
from .entities import VisualFrame
from .signals import PERSON_DETECTED


class SimulatedPerception(PerceptionModule):

    name = "simulated-perception"
    version = "0.1.0"

    def process(
        self,
        frame: VisualFrame,
    ):
        """
        Generate a controlled synthetic perception event.
        """

        person_id = f"person-{uuid4().hex[:8]}"

        return [
            create_event(
                event_type=PERSON_DETECTED,
                source=self.name,
                confidence=0.97,
                priority=1,
                data={
                    "person_id": person_id,
                    "frame_id": frame.frame_id,
                    "posture": "standing",
                    "movement": "stationary",
                },
            )
        ]