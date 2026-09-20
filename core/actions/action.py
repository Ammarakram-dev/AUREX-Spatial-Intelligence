"""
AUREX Spatial Intelligence
Intent-to-Action Orchestration Model

Phase 20
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ActionStatus(str, Enum):
    CREATED = "created"
    WAITING_CONFIRMATION = "waiting_confirmation"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ActionRisk(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ActionRequest:
    action_id: str
    action_type: str
    source_intent: str
    confidence: float
    risk: ActionRisk = ActionRisk.MEDIUM
    requires_confirmation: bool = True
    status: ActionStatus = ActionStatus.CREATED
    parameters: Dict[str, Any] = field(
        default_factory=dict
    )
    reason: str = ""
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "action_type": self.action_type,
            "source_intent": self.source_intent,
            "confidence": self.confidence,
            "risk": self.risk.value,
            "requires_confirmation": (
                self.requires_confirmation
            ),
            "status": self.status.value,
            "parameters": dict(self.parameters),
            "reason": self.reason,
            "metadata": dict(self.metadata),
        }


@dataclass
class ActionResult:
    action_id: str
    status: ActionStatus
    success: bool
    message: str
    output: Optional[Any] = None
    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_id": self.action_id,
            "status": self.status.value,
            "success": self.success,
            "message": self.message,
            "output": self.output,
            "metadata": dict(self.metadata),
        }