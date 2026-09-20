"""
AUREX Spatial Intelligence
Intent-to-Action Orchestrator

Phase 20
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional
from uuid import uuid4

from core.actions.action import (
    ActionRequest,
    ActionResult,
    ActionRisk,
    ActionStatus,
)


class AUREXActionOrchestrator:
    """
    Controlled action orchestration layer.

    Responsibilities:

    1. Convert intent proposals into action requests.
    2. Assign risk.
    3. Apply safety gates.
    4. Require confirmation when necessary.
    5. Execute only registered actions.
    6. Return structured action results.
    """

    def __init__(
        self,
        minimum_confidence: float = 0.70,
        high_risk_confidence: float = 0.90,
    ) -> None:

        self.minimum_confidence = float(
            minimum_confidence
        )

        self.high_risk_confidence = float(
            high_risk_confidence
        )

        self.adapters: Dict[
            str,
            Callable[..., Any]
        ] = {}

        self.requests: Dict[
            str,
            ActionRequest
        ] = {}

        self.history: list[
            ActionResult
        ] = []

    # ---------------------------------------------------------
    # ACTION REGISTRATION
    # ---------------------------------------------------------

    def register_action(
        self,
        action_type: str,
        handler: Callable[..., Any],
    ) -> None:
        """
        Register a safe execution adapter.
        """

        if not callable(handler):
            raise TypeError(
                "Action handler must be callable."
            )

        action_type = str(
            action_type
        ).strip().lower()

        if not action_type:
            raise ValueError(
                "Action type cannot be empty."
            )

        self.adapters[action_type] = handler

    def unregister_action(
        self,
        action_type: str,
    ) -> None:

        action_type = str(
            action_type
        ).strip().lower()

        self.adapters.pop(
            action_type,
            None,
        )

    # ---------------------------------------------------------
    # RISK
    # ---------------------------------------------------------

    def determine_risk(
        self,
        action_type: str,
    ) -> ActionRisk:

        action_type = str(
            action_type
        ).strip().lower()

        critical = {
            "emergency_workflow",
            "unlock",
            "security_override",
        }

        high = {
            "notify",
            "external_command",
            "device_control",
        }

        medium = {
            "air_canvas",
            "display",
            "request_confirmation",
        }

        if action_type in critical:
            return ActionRisk.CRITICAL

        if action_type in high:
            return ActionRisk.HIGH

        if action_type in medium:
            return ActionRisk.MEDIUM

        return ActionRisk.LOW

    # ---------------------------------------------------------
    # REQUEST CREATION
    # ---------------------------------------------------------

    def create_request(
        self,
        action_type: str,
        source_intent: str,
        confidence: float,
        requires_confirmation: bool = True,
        parameters: Optional[
            Dict[str, Any]
        ] = None,
        reason: str = "",
        metadata: Optional[
            Dict[str, Any]
        ] = None,
    ) -> ActionRequest:

        action_type = str(
            action_type
        ).strip().lower()

        source_intent = str(
            source_intent
        ).strip().lower()

        confidence = max(
            0.0,
            min(
                1.0,
                float(confidence),
            ),
        )

        risk = self.determine_risk(
            action_type
        )

        # Critical and high-risk actions
        # always require confirmation.
        if risk in {
            ActionRisk.HIGH,
            ActionRisk.CRITICAL,
        }:
            requires_confirmation = True

        request = ActionRequest(
            action_id=(
                f"act_{uuid4().hex[:12]}"
            ),
            action_type=action_type,
            source_intent=source_intent,
            confidence=confidence,
            risk=risk,
            requires_confirmation=(
                requires_confirmation
            ),
            parameters=parameters or {},
            reason=reason,
            metadata=metadata or {},
        )

        self.requests[
            request.action_id
        ] = request

        return request

    # ---------------------------------------------------------
    # SAFETY GATE
    # ---------------------------------------------------------

    def safety_check(
        self,
        request: ActionRequest,
    ) -> bool:
        """
        Determine whether an action may proceed
        to the next stage.

        This does NOT execute the action.
        """

        if request.confidence < (
            self.minimum_confidence
        ):

            request.status = (
                ActionStatus.REJECTED
            )

            request.reason = (
                "Confidence below minimum "
                "execution threshold."
            )

            return False

        if request.risk == ActionRisk.CRITICAL:

            request.requires_confirmation = True

        if request.requires_confirmation:

            request.status = (
                ActionStatus.WAITING_CONFIRMATION
            )

            request.reason = (
                "Explicit confirmation required."
            )

            return False

        request.status = (
            ActionStatus.APPROVED
        )

        return True

    # ---------------------------------------------------------
    # CONFIRMATION
    # ---------------------------------------------------------

    def confirm(
        self,
        action_id: str,
    ) -> ActionRequest:

        request = self._get_request(
            action_id
        )

        if request.status not in {
            ActionStatus.WAITING_CONFIRMATION,
            ActionStatus.CREATED,
        }:

            return request

        request.status = (
            ActionStatus.APPROVED
        )

        request.requires_confirmation = False

        request.reason = (
            "Explicit confirmation received."
        )

        return request

    def reject(
        self,
        action_id: str,
        reason: str = "Action rejected.",
    ) -> ActionRequest:

        request = self._get_request(
            action_id
        )

        request.status = (
            ActionStatus.REJECTED
        )

        request.reason = reason

        return request

    def cancel(
        self,
        action_id: str,
    ) -> ActionRequest:

        request = self._get_request(
            action_id
        )

        request.status = (
            ActionStatus.CANCELLED
        )

        request.reason = (
            "Action cancelled."
        )

        return request

    # ---------------------------------------------------------
    # EXECUTION
    # ---------------------------------------------------------

    def execute(
        self,
        action_id: str,
    ) -> ActionResult:

        request = self._get_request(
            action_id
        )

        # Never execute rejected/cancelled actions.
        if request.status in {
            ActionStatus.REJECTED,
            ActionStatus.CANCELLED,
        }:

            result = ActionResult(
                action_id=request.action_id,
                status=request.status,
                success=False,
                message=request.reason,
            )

            self.history.append(result)

            return result

        # Run safety gate if needed.
        if request.status not in {
            ActionStatus.APPROVED,
        }:

            if not self.safety_check(
                request
            ):

                result = ActionResult(
                    action_id=request.action_id,
                    status=request.status,
                    success=False,
                    message=request.reason,
                )

                self.history.append(result)

                return result

        handler = self.adapters.get(
            request.action_type
        )

        if handler is None:

            request.status = (
                ActionStatus.FAILED
            )

            request.reason = (
                "No registered action adapter."
            )

            result = ActionResult(
                action_id=request.action_id,
                status=ActionStatus.FAILED,
                success=False,
                message=request.reason,
            )

            self.history.append(result)

            return result

        request.status = (
            ActionStatus.EXECUTING
        )

        try:

            output = handler(
                **request.parameters
            )

            request.status = (
                ActionStatus.COMPLETED
            )

            result = ActionResult(
                action_id=request.action_id,
                status=ActionStatus.COMPLETED,
                success=True,
                message=(
                    "Action executed successfully."
                ),
                output=output,
            )

        except Exception as exc:

            request.status = (
                ActionStatus.FAILED
            )

            request.reason = str(exc)

            result = ActionResult(
                action_id=request.action_id,
                status=ActionStatus.FAILED,
                success=False,
                message=str(exc),
            )

        self.history.append(result)

        return result

    # ---------------------------------------------------------
    # INTENT BRIDGE
    # ---------------------------------------------------------

    def from_intent(
        self,
        intent: Any,
    ) -> ActionRequest:

        action = getattr(
            intent,
            "action",
            None,
        )

        if action is None:

            return self.create_request(
                action_type="none",
                source_intent="unknown",
                confidence=0.0,
                requires_confirmation=True,
                reason=(
                    "No action proposal "
                    "was provided."
                ),
            )

        action_type = getattr(
            action,
            "action_type",
            "none",
        )

        if hasattr(
            action_type,
            "value",
        ):
            action_type = action_type.value

        intent_type = getattr(
            action,
            "intent_type",
            "unknown",
        )

        if hasattr(
            intent_type,
            "value",
        ):
            intent_type = intent_type.value

        return self.create_request(
            action_type=str(
                action_type
            ),
            source_intent=str(
                intent_type
            ),
            confidence=float(
                getattr(
                    action,
                    "confidence",
                    0.0,
                )
            ),
            requires_confirmation=bool(
                getattr(
                    action,
                    "requires_confirmation",
                    True,
                )
            ),
            reason=str(
                getattr(
                    action,
                    "reason",
                    "",
                )
            ),
        )

    # ---------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------

    def _get_request(
        self,
        action_id: str,
    ) -> ActionRequest:

        action_id = str(
            action_id
        )

        request = self.requests.get(
            action_id
        )

        if request is None:
            raise KeyError(
                f"Unknown action ID: {action_id}"
            )

        return request

    def get_request(
        self,
        action_id: str,
    ) -> Optional[ActionRequest]:

        return self.requests.get(
            str(action_id)
        )

    def status(self) -> Dict[str, Any]:

        return {
            "engine": (
                "AUREXActionOrchestrator"
            ),
            "registered_actions": sorted(
                self.adapters.keys()
            ),
            "pending_requests": sum(
                1
                for request in self.requests.values()
                if request.status
                == ActionStatus.WAITING_CONFIRMATION
            ),
            "history_count": len(
                self.history
            ),
            "minimum_confidence": (
                self.minimum_confidence
            ),
            "high_risk_confidence": (
                self.high_risk_confidence
            ),
            "status": "ready",
        }