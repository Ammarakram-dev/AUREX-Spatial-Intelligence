from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class MultimodalDecision:

    intent: str
    confidence: float
    sources: List[str] = field(
        default_factory=list
    )

    voice_text: Optional[str] = None

    context_type: Optional[str] = None

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:

        return {
            "intent": self.intent,
            "confidence": self.confidence,
            "sources": list(self.sources),
            "voice_text": self.voice_text,
            "context_type": self.context_type,
            "metadata": dict(self.metadata),
        }


class AUREXMultimodalFusion:

    def __init__(
        self,
        minimum_confidence: float = 0.55,
    ) -> None:

        self.minimum_confidence = (
            minimum_confidence
        )

        self.history: List[
            MultimodalDecision
        ] = []

    @staticmethod
    def _value(obj, name, default=None):

        return getattr(
            obj,
            name,
            default,
        )

    def combine(
        self,
        voice_command=None,
        context=None,
        intent=None,
        hazard=None,
        gesture_intent=None,
    ) -> MultimodalDecision:

        candidates = []

        sources = []

        # -----------------------------------------------------
        # Voice
        # -----------------------------------------------------

        if voice_command is not None:

            voice_intent = getattr(
                getattr(
                    voice_command,
                    "intent",
                    None,
                ),
                "value",
                str(
                    getattr(
                        voice_command,
                        "intent",
                        "unknown",
                    )
                ),
            )

            voice_confidence = float(
                getattr(
                    voice_command,
                    "confidence",
                    0.0,
                )
            )

            if voice_intent != "unknown":

                candidates.append(
                    (
                        voice_intent,
                        voice_confidence,
                        "voice",
                    )
                )

                sources.append("voice")

        # -----------------------------------------------------
        # Existing intent engine
        # -----------------------------------------------------

        if intent is not None:

            primary = getattr(
                intent,
                "primary",
                None,
            )

            if primary is not None:

                intent_type = getattr(
                    primary,
                    "intent_type",
                    "unknown",
                )

                intent_value = getattr(
                    intent_type,
                    "value",
                    str(intent_type),
                )

                confidence = float(
                    getattr(
                        primary,
                        "confidence",
                        0.0,
                    )
                )

                candidates.append(
                    (
                        intent_value,
                        confidence,
                        "vision",
                    )
                )

                sources.append("vision")

        # -----------------------------------------------------
        # Gesture
        # -----------------------------------------------------

        if gesture_intent is not None:

            gesture_value = getattr(
                gesture_intent,
                "value",
                str(gesture_intent),
            )

            candidates.append(
                (
                    gesture_value,
                    0.70,
                    "gesture",
                )
            )

            sources.append("gesture")

        # -----------------------------------------------------
        # Context
        # -----------------------------------------------------

        context_type = None

        if context is not None:

            context_value = getattr(
                getattr(
                    context,
                    "context_type",
                    None,
                ),
                "value",
                str(
                    getattr(
                        context,
                        "context_type",
                        "unknown",
                    )
                ),
            )

            context_type = context_value

        # -----------------------------------------------------
        # Resolve
        # -----------------------------------------------------

        if not candidates:

            decision = MultimodalDecision(
                intent="unknown",
                confidence=0.0,
                sources=[],
                context_type=context_type,
            )

            self.history.append(
                decision
            )

            return decision

        # Voice receives priority when explicit,
        # otherwise strongest available signal.
        candidates.sort(
            key=lambda item: item[1],
            reverse=True,
        )

        best_intent, best_confidence, best_source = (
            candidates[0]
        )

        # Agreement between modalities increases confidence.
        agreeing = sum(
            1
            for candidate in candidates
            if candidate[0] == best_intent
        )

        if agreeing >= 2:

            best_confidence = min(
                1.0,
                best_confidence + 0.10,
            )

        decision = MultimodalDecision(
            intent=best_intent,
            confidence=best_confidence,
            sources=list(
                dict.fromkeys(sources)
            ),
            voice_text=(
                getattr(
                    voice_command,
                    "text",
                    None,
                )
                if voice_command is not None
                else None
            ),
            context_type=context_type,
            metadata={
                "primary_source": best_source,
                "agreement_count": agreeing,
                "candidate_count": len(
                    candidates
                ),
                "hazard_present": (
                    hazard is not None
                ),
            },
        )

        self.history.append(
            decision
        )

        return decision

    def reset(self) -> None:
        self.history.clear()

    def status(self) -> Dict[str, Any]:

        return {
            "history_size": len(
                self.history
            ),
            "latest": (
                self.history[-1].to_dict()
                if self.history
                else None
            ),
        }