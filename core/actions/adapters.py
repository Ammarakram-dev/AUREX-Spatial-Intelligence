"""
AUREX Spatial Intelligence
Safe Action Adapters

Phase 20
"""

from __future__ import annotations

from typing import Any, Dict


def display_action(
    message: str = "",
    **kwargs: Any,
) -> Dict[str, Any]:

    return {
        "type": "display",
        "message": message,
        "status": "displayed",
    }


def air_canvas_action(
    command: str = "noop",
    **kwargs: Any,
) -> Dict[str, Any]:

    return {
        "type": "air_canvas",
        "command": command,
        "status": "prepared",
    }


def notification_action(
    message: str = "AUREX notification",
    **kwargs: Any,
) -> Dict[str, Any]:

    return {
        "type": "notify",
        "message": message,
        "status": "prepared",
    }


def emergency_workflow_action(
    event: str = "emergency",
    **kwargs: Any,
) -> Dict[str, Any]:

    return {
        "type": "emergency_workflow",
        "event": event,
        "status": "prepared",
        "requires_external_handler": True,
    }


def request_confirmation_action(
    **kwargs: Any,
) -> Dict[str, Any]:

    return {
        "type": "request_confirmation",
        "status": "confirmation_requested",
    }


def register_default_actions(
    orchestrator: Any,
) -> None:

    orchestrator.register_action(
        "display",
        display_action,
    )

    orchestrator.register_action(
        "air_canvas",
        air_canvas_action,
    )

    orchestrator.register_action(
        "notify",
        notification_action,
    )

    orchestrator.register_action(
        "emergency_workflow",
        emergency_workflow_action,
    )

    orchestrator.register_action(
        "request_confirmation",
        request_confirmation_action,
    )