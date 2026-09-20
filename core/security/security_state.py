"""
AUREX Spatial Intelligence
Security State Models

Phase 21
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class SecurityState(str, Enum):
    UNKNOWN = "unknown"
    NO_PRESENCE = "no_presence"
    PRESENCE_DETECTED = "presence_detected"
    VERIFYING = "verifying"
    TRUSTED = "trusted"
    SUSPICIOUS = "suspicious"
    DENIED = "denied"
    LOCKED = "locked"


class SecurityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityDecision:
    state: SecurityState
    level: SecurityLevel
    confidence: float
    authorized: bool
    requires_verification: bool
    reasons: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "level": self.level.value,
            "confidence": self.confidence,
            "authorized": self.authorized,
            "requires_verification": self.requires_verification,
            "reasons": list(self.reasons),
            "metadata": dict(self.metadata),
        }

    def status(self) -> Dict[str, Any]:
        return self.to_dict()