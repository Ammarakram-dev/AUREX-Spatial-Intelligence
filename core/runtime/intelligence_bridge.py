from __future__ import annotations

from typing import Any, Iterable, Optional

from core.intelligence.situation import (
    AUREXUnifiedIntelligence,
)


class AUREXIntelligenceBridge:
    """
    Connects the central AUREX runtime with the
    unified intelligence layer from Step 1.
    """

    def __init__(self):
        self.intelligence = AUREXUnifiedIntelligence()

    def process(
        self,
        context: Any = None,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
        scene: Any = None,
        security: Any = None,
        hazard: Any = None,
        behavior: Any = None,
        affect: Any = None,
        prediction: Any = None,
        intent: Any = None,
        multimodal: Any = None,
        memory: Any = None,
    ):
        return self.intelligence.update(
            context=context,
            human_states=human_states,
            relationships=relationships,
            scene=scene,
            security=security,
            hazard=hazard,
            behavior=behavior,
            affect=affect,
            prediction=prediction,
            intent=intent,
            multimodal=multimodal,
            memory=memory,
        )

    def reset(self):
        self.intelligence.reset()

    def status(self):
        return self.intelligence.status()