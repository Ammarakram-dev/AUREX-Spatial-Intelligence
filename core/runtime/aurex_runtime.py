from __future__ import annotations

from typing import Any, Callable, Dict, Optional
import time

from .runtime_state import (
    ModuleState,
    ModuleStatus,
    RuntimeSnapshot,
    RuntimeState,
)
from .audit import AUREXAuditLogger


class AUREXRuntime:
    """
    Central runtime coordinator for AUREX.

    This layer coordinates modules but does not replace them.
    Individual intelligence modules remain responsible for their
    own domain logic.
    """

    def __init__(self):
        self.state = RuntimeState.STOPPED

        self.modules: Dict[str, ModuleStatus] = {}
        self.handlers: Dict[str, Callable[..., Any]] = {}

        self.audit = AUREXAuditLogger()

        self.cycle_count = 0
        self.successful_cycles = 0
        self.failed_cycles = 0

        self.total_cycle_time = 0.0
        self.last_cycle_time = 0.0

        self.current_world_state: Any = None
        self.last_error = ""

        self.snapshot = RuntimeSnapshot()

    # ---------------------------------------------------------
    # Module management
    # ---------------------------------------------------------

    def register_module(
        self,
        name: str,
        handler: Optional[Callable[..., Any]] = None,
        enabled: bool = True,
    ) -> ModuleStatus:

        status = ModuleStatus(
            name=name,
            enabled=enabled,
            state=ModuleState.READY if enabled else ModuleState.STOPPED,
        )

        self.modules[name] = status

        if handler is not None:
            self.handlers[name] = handler

        self.audit.record(
            event="module_registered",
            source="runtime",
            message=name,
        )

        return status

    def unregister_module(self, name: str) -> bool:
        if name not in self.modules:
            return False

        self.modules.pop(name, None)
        self.handlers.pop(name, None)

        self.audit.record(
            event="module_unregistered",
            source="runtime",
            message=name,
        )

        return True

    def enable_module(self, name: str) -> bool:
        module = self.modules.get(name)

        if module is None:
            return False

        module.enabled = True
        module.state = ModuleState.READY

        return True

    def disable_module(self, name: str) -> bool:
        module = self.modules.get(name)

        if module is None:
            return False

        module.enabled = False
        module.state = ModuleState.STOPPED

        return True

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(self) -> bool:
        if self.state == RuntimeState.RUNNING:
            return True

        self.state = RuntimeState.STARTING

        self.audit.record(
            event="runtime_starting",
            source="runtime",
        )

        try:
            for module in self.modules.values():
                if module.enabled:
                    module.mark_ready("Runtime initialized.")

            self.state = RuntimeState.RUNNING

            self.audit.record(
                event="runtime_started",
                source="runtime",
            )

            self._refresh_snapshot()

            return True

        except Exception as exc:
            self.last_error = str(exc)
            self.state = RuntimeState.ERROR

            self.audit.record(
                event="runtime_start_failed",
                source="runtime",
                severity="error",
                message=str(exc),
            )

            return False

    def pause(self) -> bool:
        if self.state != RuntimeState.RUNNING:
            return False

        self.state = RuntimeState.PAUSED

        self.audit.record(
            event="runtime_paused",
            source="runtime",
        )

        return True

    def resume(self) -> bool:
        if self.state != RuntimeState.PAUSED:
            return False

        self.state = RuntimeState.RUNNING

        self.audit.record(
            event="runtime_resumed",
            source="runtime",
        )

        return True

    def stop(self) -> bool:
        if self.state == RuntimeState.STOPPED:
            return True

        self.state = RuntimeState.STOPPING

        for module in self.modules.values():
            module.state = ModuleState.STOPPED

        self.state = RuntimeState.STOPPED

        self.audit.record(
            event="runtime_stopped",
            source="runtime",
        )

        self._refresh_snapshot()

        return True

    # ---------------------------------------------------------
    # Execution
    # ---------------------------------------------------------

    def execute_module(
        self,
        name: str,
        *args,
        **kwargs,
    ) -> Any:

        module = self.modules.get(name)

        if module is None:
            raise KeyError(f"Module not registered: {name}")

        if not module.enabled:
            return None

        handler = self.handlers.get(name)

        if handler is None:
            module.mark_update("No execution handler registered.")
            return None

        started = time.perf_counter()

        try:
            result = handler(*args, **kwargs)

            elapsed = (time.perf_counter() - started) * 1000.0

            module.mark_update(
                f"Execution completed in {elapsed:.2f} ms."
            )

            return result

        except Exception as exc:
            module.mark_error(str(exc))

            self.audit.record(
                event="module_error",
                source=name,
                severity="error",
                message=str(exc),
            )

            raise

    def execute_cycle(
        self,
        cycle_handler: Callable[[], Any],
    ) -> Any:

        if self.state != RuntimeState.RUNNING:
            raise RuntimeError(
                f"Runtime is not running: {self.state.value}"
            )

        started = time.perf_counter()

        self.cycle_count += 1

        try:
            result = cycle_handler()

            elapsed = (time.perf_counter() - started) * 1000.0

            self.last_cycle_time = elapsed
            self.total_cycle_time += elapsed
            self.successful_cycles += 1

            self.current_world_state = result

            self._update_snapshot_from_world(result)

            return result

        except Exception as exc:
            elapsed = (time.perf_counter() - started) * 1000.0

            self.last_cycle_time = elapsed
            self.total_cycle_time += elapsed
            self.failed_cycles += 1
            self.last_error = str(exc)

            self.state = RuntimeState.DEGRADED

            self.audit.record(
                event="cycle_failed",
                source="runtime",
                severity="error",
                message=str(exc),
            )

            self._refresh_snapshot()

            raise

    # ---------------------------------------------------------
    # Monitoring
    # ---------------------------------------------------------

    def _update_snapshot_from_world(self, world: Any) -> None:
        self._refresh_snapshot()

        if world is None:
            return

        if hasattr(world, "people_count"):
            self.snapshot.people_count = int(
                getattr(world, "people_count", 0)
            )

        if hasattr(world, "object_count"):
            self.snapshot.object_count = int(
                getattr(world, "object_count", 0)
            )

        situation = getattr(world, "situation", None)

        if situation is not None:
            self.snapshot.situation = (
                situation.value
                if hasattr(situation, "value")
                else str(situation)
            )

        priority = getattr(world, "priority", None)

        if priority is not None:
            self.snapshot.priority = (
                priority.value
                if hasattr(priority, "value")
                else str(priority)
            )

        security_state = getattr(world, "security_state", None)

        if security_state is not None:
            self.snapshot.security_state = str(
                security_state
            )

    def _refresh_snapshot(self) -> None:
        active = sum(
            1
            for module in self.modules.values()
            if module.enabled
            and module.state not in {
                ModuleState.ERROR,
                ModuleState.STOPPED,
            }
        )

        failed = sum(
            1
            for module in self.modules.values()
            if module.state == ModuleState.ERROR
        )

        average = 0.0

        if self.cycle_count > 0:
            average = (
                self.total_cycle_time / self.cycle_count
            )

        self.snapshot.state = self.state
        self.snapshot.timestamp = time.time()

        self.snapshot.cycle_count = self.cycle_count
        self.snapshot.successful_cycles = self.successful_cycles
        self.snapshot.failed_cycles = self.failed_cycles

        self.snapshot.cycle_time_ms = self.last_cycle_time
        self.snapshot.average_cycle_time_ms = average

        self.snapshot.active_modules = active
        self.snapshot.failed_modules = failed

        self.snapshot.last_error = self.last_error

    def status(self) -> Dict[str, Any]:
        self._refresh_snapshot()

        return {
            "runtime": self.snapshot.to_dict(),
            "modules": {
                name: module.to_dict()
                for name, module in self.modules.items()
            },
            "audit": self.audit.status(),
        }