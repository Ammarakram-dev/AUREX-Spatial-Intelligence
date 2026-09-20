from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict
import time


class RuntimeState(str, Enum):
    STOPPED = "stopped"
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    DEGRADED = "degraded"
    ERROR = "error"
    STOPPING = "stopping"


class ModuleState(str, Enum):
    UNKNOWN = "unknown"
    READY = "ready"
    RUNNING = "running"
    DEGRADED = "degraded"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class ModuleStatus:
    name: str
    state: ModuleState = ModuleState.UNKNOWN
    enabled: bool = True
    last_update: float = 0.0
    update_count: int = 0
    error_count: int = 0
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def mark_update(self, message: str = "") -> None:
        self.state = ModuleState.RUNNING
        self.last_update = time.time()
        self.update_count += 1
        self.message = message

    def mark_ready(self, message: str = "") -> None:
        self.state = ModuleState.READY
        self.message = message

    def mark_error(self, message: str = "") -> None:
        self.state = ModuleState.ERROR
        self.error_count += 1
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state.value,
            "enabled": self.enabled,
            "last_update": self.last_update,
            "update_count": self.update_count,
            "error_count": self.error_count,
            "message": self.message,
            "metadata": self.metadata,
        }


@dataclass
class RuntimeSnapshot:
    state: RuntimeState = RuntimeState.STOPPED
    timestamp: float = field(default_factory=time.time)

    cycle_count: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0

    cycle_time_ms: float = 0.0
    average_cycle_time_ms: float = 0.0

    active_modules: int = 0
    failed_modules: int = 0

    people_count: int = 0
    object_count: int = 0

    situation: str = "unknown"
    priority: str = "normal"
    security_state: str = "unknown"

    last_error: str = ""

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "state": self.state.value,
            "timestamp": self.timestamp,
            "cycle_count": self.cycle_count,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
            "cycle_time_ms": self.cycle_time_ms,
            "average_cycle_time_ms": self.average_cycle_time_ms,
            "active_modules": self.active_modules,
            "failed_modules": self.failed_modules,
            "people_count": self.people_count,
            "object_count": self.object_count,
            "situation": self.situation,
            "priority": self.priority,
            "security_state": self.security_state,
            "last_error": self.last_error,
            "metadata": self.metadata,
        }