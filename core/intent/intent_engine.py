"""
AUREX Spatial Intelligence
Intent Inference Engine
Phase 19
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from core.intent.intent import (
    ActionProposal,
    ActionType,
    AUREXIntent,
    IntentCandidate,
    IntentType,
)


class AUREXIntentEngine:
    """
    Multimodal intent inference layer.

    Important:
    Intent inference produces candidates and proposed
    actions. It does not blindly execute actions.
    """

    def __init__(
        self,
        minimum_confidence: float = 0.55,
        confirmation_threshold: float = 0.80,
    ) -> None:

        self.minimum_confidence = float(
            minimum_confidence
        )

        self.confirmation_threshold = float(
            confirmation_threshold
        )

    @staticmethod
    def _get(
        obj: Any,
        name: str,
        default: Any = None,
    ) -> Any:

        if isinstance(obj, dict):
            return obj.get(name, default)

        return getattr(obj, name, default)

    @staticmethod
    def _normalize(value: Any) -> str:

        if value is None:
            return ""

        if hasattr(value, "value"):
            value = value.value

        return str(value).strip().lower()

    @staticmethod
    def _confidence(
        value: Any,
        default: float = 1.0,
    ) -> float:

        try:
            value = float(value)
        except (
            TypeError,
            ValueError,
        ):
            value = default

        return max(
            0.0,
            min(1.0, value),
        )

    def _candidate(
        self,
        intent_type: IntentType,
        priority: int,
        action: ActionType,
        confirmation: bool = True,
    ) -> IntentCandidate:

        return IntentCandidate(
            intent_type=intent_type,
            priority=priority,
            proposed_action=action,
            requires_confirmation=confirmation,
        )

    def infer(
        self,
        context: Optional[Any] = None,
        gestures: Optional[Iterable[Any]] = None,
        voice_intents: Optional[Iterable[Any]] = None,
        human_states: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
    ) -> AUREXIntent:

        candidates: List[IntentCandidate] = []

        context_type = self._normalize(
            self._get(
                context,
                "context_type",
                "unknown",
            )
        )

        # -------------------------------------------------
        # CONTEXT SIGNALS
        # -------------------------------------------------

        if context_type in {
            "person_approaching",
            "approaching",
        }:

            candidate = self._candidate(
                IntentType.APPROACH,
                priority=40,
                action=ActionType.DISPLAY,
            )

            candidate.add_evidence(
                "context",
                context_type,
                confidence=self._confidence(
                    self._get(
                        context,
                        "confidence",
                        0.7,
                    )
                ),
                weight=0.9,
            )

            candidates.append(candidate)

        if context_type in {
            "person_moving_away",
            "moving_away",
        }:

            candidate = self._candidate(
                IntentType.MOVE_AWAY,
                priority=30,
                action=ActionType.DISPLAY,
            )

            candidate.add_evidence(
                "context",
                context_type,
                confidence=self._confidence(
                    self._get(
                        context,
                        "confidence",
                        0.7,
                    )
                ),
                weight=0.8,
            )

            candidates.append(candidate)

        # -------------------------------------------------
        # GESTURE SIGNALS
        # -------------------------------------------------

        for gesture in gestures or []:

            if isinstance(gesture, str):

                gesture_name = self._normalize(
                    gesture
                )

                gesture_confidence = 0.80

            else:

                gesture_name = self._normalize(
                    self._get(
                        gesture,
                        "gesture",
                        self._get(
                            gesture,
                            "name",
                            self._get(
                                gesture,
                                "label",
                                "",
                            ),
                        ),
                    )
                )

                gesture_confidence = self._confidence(
                    self._get(
                        gesture,
                        "confidence",
                        0.80,
                    )
                )

            if gesture_name in {
                "draw",
                "air_draw",
                "writing",
            }:

                candidate = self._candidate(
                    IntentType.AIR_DRAW,
                    priority=60,
                    action=ActionType.AIR_CANVAS,
                )

                candidate.add_evidence(
                    "gesture",
                    gesture_name,
                    gesture_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif gesture_name in {
                "select",
                "pinch",
                "air_select",
            }:

                candidate = self._candidate(
                    IntentType.AIR_SELECT,
                    priority=65,
                    action=ActionType.AIR_CANVAS,
                )

                candidate.add_evidence(
                    "gesture",
                    gesture_name,
                    gesture_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif gesture_name in {
                "clear",
                "erase",
                "air_clear",
            }:

                candidate = self._candidate(
                    IntentType.AIR_CLEAR,
                    priority=70,
                    action=ActionType.AIR_CANVAS,
                )

                candidate.add_evidence(
                    "gesture",
                    gesture_name,
                    gesture_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif gesture_name in {
                "help",
                "request_help",
            }:

                candidate = self._candidate(
                    IntentType.REQUEST_HELP,
                    priority=90,
                    action=ActionType.NOTIFY,
                )

                candidate.add_evidence(
                    "gesture",
                    gesture_name,
                    gesture_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif gesture_name in {
                "emergency",
                "sos",
            }:

                candidate = self._candidate(
                    IntentType.EMERGENCY,
                    priority=100,
                    action=ActionType.EMERGENCY_WORKFLOW,
                )

                candidate.add_evidence(
                    "gesture",
                    gesture_name,
                    gesture_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

        # -------------------------------------------------
        # VOICE SIGNALS
        # -------------------------------------------------

        for voice in voice_intents or []:

            if isinstance(voice, str):

                voice_name = self._normalize(
                    voice
                )

                voice_confidence = 0.80

            else:

                voice_name = self._normalize(
                    self._get(
                        voice,
                        "intent",
                        self._get(
                            voice,
                            "name",
                            self._get(
                                voice,
                                "command",
                                "",
                            ),
                        ),
                    )
                )

                voice_confidence = self._confidence(
                    self._get(
                        voice,
                        "confidence",
                        0.80,
                    )
                )

            if voice_name in {
                "draw",
                "air_draw",
            }:

                candidate = self._candidate(
                    IntentType.AIR_DRAW,
                    priority=60,
                    action=ActionType.AIR_CANVAS,
                )

                candidate.add_evidence(
                    "voice",
                    voice_name,
                    voice_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif voice_name in {
                "select",
                "air_select",
            }:

                candidate = self._candidate(
                    IntentType.AIR_SELECT,
                    priority=65,
                    action=ActionType.AIR_CANVAS,
                )

                candidate.add_evidence(
                    "voice",
                    voice_name,
                    voice_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif voice_name in {
                "clear",
                "erase",
            }:

                candidate = self._candidate(
                    IntentType.AIR_CLEAR,
                    priority=70,
                    action=ActionType.AIR_CANVAS,
                )

                candidate.add_evidence(
                    "voice",
                    voice_name,
                    voice_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif voice_name in {
                "help",
                "request_help",
            }:

                candidate = self._candidate(
                    IntentType.REQUEST_HELP,
                    priority=90,
                    action=ActionType.NOTIFY,
                )

                candidate.add_evidence(
                    "voice",
                    voice_name,
                    voice_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

            elif voice_name in {
                "emergency",
                "sos",
            }:

                candidate = self._candidate(
                    IntentType.EMERGENCY,
                    priority=100,
                    action=ActionType.EMERGENCY_WORKFLOW,
                )

                candidate.add_evidence(
                    "voice",
                    voice_name,
                    voice_confidence,
                    weight=1.0,
                )

                candidates.append(candidate)

        # -------------------------------------------------
        # HUMAN MOVEMENT
        # -------------------------------------------------

        for person in human_states or []:

            person_id = str(
                self._get(
                    person,
                    "person_id",
                    "unknown",
                )
            )

            direction = self._normalize(
                self._get(
                    person,
                    "movement_direction",
                    "",
                )
            )

            distance = self._get(
                person,
                "movement_distance",
                0.0,
            )

            confidence = self._confidence(
                self._get(
                    person,
                    "detection_confidence",
                    0.75,
                )
            )

            try:
                distance = abs(float(distance))
            except (
                TypeError,
                ValueError,
            ):
                distance = 0.0

            if direction in {
                "approaching",
                "toward",
                "towards",
            }:

                candidate = self._candidate(
                    IntentType.APPROACH,
                    priority=40,
                    action=ActionType.DISPLAY,
                )

                candidate.add_evidence(
                    "movement",
                    direction,
                    confidence,
                    weight=0.8,
                    metadata={
                        "person_id": person_id,
                        "movement_distance": distance,
                    },
                )

                candidates.append(candidate)

        # -------------------------------------------------
        # RELATIONSHIPS
        # -------------------------------------------------

        for relationship in relationships or []:

            relation = self._normalize(
                self._get(
                    relationship,
                    "relationship",
                    self._get(
                        relationship,
                        "type",
                        "",
                    ),
                )
            )

            confidence = self._confidence(
                self._get(
                    relationship,
                    "confidence",
                    0.70,
                )
            )

            if relation == "approaching":

                candidate = self._candidate(
                    IntentType.APPROACH,
                    priority=45,
                    action=ActionType.DISPLAY,
                )

                candidate.add_evidence(
                    "spatial_relationship",
                    relation,
                    confidence,
                    weight=0.85,
                )

                candidates.append(candidate)

        # -------------------------------------------------
        # FALLBACK
        # -------------------------------------------------

        if not candidates:

            candidate = self._candidate(
                IntentType.OBSERVE,
                priority=10,
                action=ActionType.NONE,
                confirmation=False,
            )

            candidate.add_evidence(
                "system",
                "no_strong_intent_signal",
                confidence=0.70,
                weight=0.5,
            )

            candidates.append(candidate)

        # -------------------------------------------------
        # MERGE SAME INTENTS
        # -------------------------------------------------

        merged: Dict[
            IntentType,
            IntentCandidate
        ] = {}

        for candidate in candidates:

            existing = merged.get(
                candidate.intent_type
            )

            if existing is None:

                merged[
                    candidate.intent_type
                ] = candidate

            else:

                existing.evidence.extend(
                    candidate.evidence
                )

                existing.priority = max(
                    existing.priority,
                    candidate.priority,
                )

                existing.requires_confirmation = (
                    existing.requires_confirmation
                    or candidate.requires_confirmation
                )

        final_candidates = list(
            merged.values()
        )

        for candidate in final_candidates:

            candidate.calculate_confidence()

        # Highest priority first, then confidence.

        final_candidates.sort(
            key=lambda item: (
                item.priority,
                item.confidence,
            ),
            reverse=True,
        )

        primary = final_candidates[0]

        # Low-confidence candidates become observe.

        if (
            primary.confidence
            < self.minimum_confidence
        ):

            primary = self._candidate(
                IntentType.OBSERVE,
                priority=5,
                action=ActionType.NONE,
                confirmation=False,
            )

            primary.add_evidence(
                "safety_filter",
                "intent_below_threshold",
                confidence=0.90,
            )

            primary.calculate_confidence()

        action = self._build_action(
            primary
        )

        return AUREXIntent(
            primary=primary,
            candidates=final_candidates,
            action=action,
            context_type=context_type,
        )

    def _build_action(
        self,
        candidate: IntentCandidate,
    ) -> ActionProposal:

        requires_confirmation = (
            candidate.requires_confirmation
            or candidate.confidence
            < self.confirmation_threshold
        )

        return ActionProposal(
            action_type=candidate.proposed_action,
            intent_type=candidate.intent_type,
            confidence=candidate.confidence,
            requires_confirmation=(
                requires_confirmation
            ),
            approved=False,
            reason=(
                "Intent inferred; action requires "
                "explicit safety gate."
            ),
        )

    def approve(
        self,
        intent: AUREXIntent,
    ) -> ActionProposal:

        if intent.action is None:

            intent.action = ActionProposal(
                action_type=ActionType.NONE,
                intent_type=IntentType.UNKNOWN,
                confidence=0.0,
                requires_confirmation=True,
                approved=False,
                reason="No action proposal.",
            )

            return intent.action

        if (
            intent.action.confidence
            < self.minimum_confidence
        ):

            intent.action.approved = False

            intent.action.reason = (
                "Confidence below execution threshold."
            )

            return intent.action

        if intent.action.requires_confirmation:

            intent.action.approved = False

            intent.action.reason = (
                "Explicit confirmation required."
            )

            return intent.action

        intent.action.approved = True

        intent.action.reason = (
            "Action passed the current safety gate."
        )

        return intent.action

    def status(self) -> Dict[str, Any]:

        return {
            "engine": "AUREXIntentEngine",
            "minimum_confidence": (
                self.minimum_confidence
            ),
            "confirmation_threshold": (
                self.confirmation_threshold
            ),
            "status": "ready",
        }