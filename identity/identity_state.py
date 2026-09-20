"""
AUREX Spatial Intelligence
Identity State Models

Phase 22
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class IdentityState(str, Enum):
    UNKNOWN = "unknown"
    NO_FACE = "no_face"
    FACE_PRESENT = "face_present"
    LIVENESS_CHECK = "liveness_check"
    VERIFYING = "verifying"
    VERIFIED = "verified"
    REJECTED = "rejected"


class LivenessState(str, Enum):
    UNKNOWN = "unknown"
    NOT_PRESENT = "not_present"
    POSSIBLE_SPOOF = "possible_spoof"
    LIVE = "live"


@dataclass
class IdentityDecision:
    state: IdentityState
    liveness_state: LivenessState
    confidence: float
    verified: bool
    requires_more_evidence: bool
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "liveness_state": self.liveness_state.value,
            "confidence": self.confidence,
            "verified": self.verified,
            "requires_more_evidence": (
                self.requires_more_evidence
            ),
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return self.to_dict()