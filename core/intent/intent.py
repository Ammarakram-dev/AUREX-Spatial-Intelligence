"""
AUREX Spatial Intelligence
Intent Intelligence Model
Phase 19
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class IntentType(str, Enum):
    UNKNOWN = "unknown"

    OBSERVE = "observe"
    APPROACH = "approach"
    MOVE_AWAY = "move_away"

    AIR_DRAW = "air_draw"
    AIR_SELECT = "air_select"
    AIR_CLEAR = "air_clear"
    AIR_CONTROL = "air_control"

    INTERACT = "interact"
    REQUEST_HELP = "request_help"
    EMERGENCY = "emergency"


class ActionType(str, Enum):
    NONE = "none"
    DISPLAY = "display"
    AIR_CANVAS = "air_canvas"
    NOTIFY = "notify"
    EMERGENCY_WORKFLOW = "emergency_workflow"
    REQUEST_CONFIRMATION = "request_confirmation"


@dataclass
class IntentEvidence:
    source: str
    value: Any
    confidence: float = 1.0
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def score(self) -> float:
        return max(
            0.0,
            min(
                1.0,
                float(self.confidence) * float(self.weight),
            ),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "value": self.value,
            "confidence": self.confidence,
            "weight": self.weight,
            "score": self.score(),
            "metadata": dict(self.metadata),
        }


@dataclass
class IntentCandidate:
    intent_type: IntentType
    confidence: float = 0.0
    evidence: List[IntentEvidence] = field(
        default_factory=list
    )
    priority: int = 0
    requires_confirmation: bool = True
    proposed_action: ActionType = ActionType.NONE

    def add_evidence(
        self,
        source: str,
        value: Any,
        confidence: float = 1.0,
        weight: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:

        confidence = max(
            0.0,
            min(1.0, float(confidence)),
        )

        self.evidence.append(
            IntentEvidence(
                source=source,
                value=value,
                confidence=confidence,
                weight=weight,
                metadata=metadata or {},
            )
        )

    def calculate_confidence(self) -> float:

        if not self.evidence:
            self.confidence = 0.0
            return self.confidence

        scores = [
            evidence.score()
            for evidence in self.evidence
        ]

        average = sum(scores) / len(scores)

        support_bonus = min(
            0.15,
            max(0, len(scores) - 1) * 0.03,
        )

        self.confidence = max(
            0.0,
            min(
                1.0,
                average + support_bonus,
            ),
        )

        return self.confidence

    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "priority": self.priority,
            "requires_confirmation": (
                self.requires_confirmation
            ),
            "proposed_action": (
                self.proposed_action.value
            ),
            "evidence": [
                item.to_dict()
                for item in self.evidence
            ],
        }


@dataclass
class ActionProposal:
    action_type: ActionType
    intent_type: IntentType
    confidence: float
    requires_confirmation: bool = True
    approved: bool = False
    reason: str = ""
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type.value,
            "intent_type": self.intent_type.value,
            "confidence": self.confidence,
            "requires_confirmation": (
                self.requires_confirmation
            ),
            "approved": self.approved,
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


@dataclass
class AUREXIntent:
    primary: IntentCandidate

    candidates: List[IntentCandidate] = field(
        default_factory=list
    )

    action: Optional[ActionProposal] = None

    context_type: str = "unknown"

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "primary": self.primary.to_dict(),
            "candidates": [
                candidate.to_dict()
                for candidate in self.candidates
            ],
            "action": (
                self.action.to_dict()
                if self.action
                else None
            ),
            "context_type": self.context_type,
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return {
            "primary_intent": (
                self.primary.intent_type.value
            ),
            "confidence": self.primary.confidence,
            "action": (
                self.action.action_type.value
                if self.action
                else ActionType.NONE.value
            ),
            "requires_confirmation": (
                self.action.requires_confirmation
                if self.action
                else True
            ),
        }