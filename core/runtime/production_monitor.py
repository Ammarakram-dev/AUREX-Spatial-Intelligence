from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any

from config.production import production_config


@dataclass
class HealthCheck:
    name: str
    status: str = "unknown"
    message: str = ""
    duration_ms: float = 0.0
    timestamp: float = field(
        default_factory=time.time
    )

    @property
    def healthy(self) -> bool:
        return self.status == "healthy"


@dataclass
class RuntimeMetrics:
    started_at: float | None = None
    stopped_at: float | None = None

    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0

    total_cycle_time_ms: float = 0.0
    max_cycle_time_ms: float = 0.0

    runtime_errors: int = 0

    def record_cycle(
        self,
        duration_ms: float,
        success: bool,
    ) -> None:
        self.total_cycles += 1
        self.total_cycle_time_ms += duration_ms

        if duration_ms > self.max_cycle_time_ms:
            self.max_cycle_time_ms = duration_ms

        if success:
            self.successful_cycles += 1
        else:
            self.failed_cycles += 1
            self.runtime_errors += 1

    @property
    def average_cycle_time_ms(self) -> float:
        if self.total_cycles == 0:
            return 0.0

        return (
            self.total_cycle_time_ms
            / self.total_cycles
        )

    @property
    def success_rate(self) -> float:
        if self.total_cycles == 0:
            return 0.0

        return (
            self.successful_cycles
            / self.total_cycles
        ) * 100.0

    def snapshot(self) -> dict[str, Any]:
        return {
            "started_at": self.started_at,
            "stopped_at": self.stopped_at,
            "total_cycles": self.total_cycles,
            "successful_cycles": self.successful_cycles,
            "failed_cycles": self.failed_cycles,
            "average_cycle_time_ms": (
                self.average_cycle_time_ms
            ),
            "max_cycle_time_ms": (
                self.max_cycle_time_ms
            ),
            "runtime_errors": self.runtime_errors,
            "success_rate": self.success_rate,
        }


class AUREXProductionMonitor:
    """
    Production monitoring layer for AUREX.

    Provides:
    - runtime metrics
    - health checks
    - operational status
    - structured logging
    - thread-safe metric updates
    """

    def __init__(self) -> None:
        self.config = production_config

        self.metrics = RuntimeMetrics()

        self._health_checks: dict[
            str,
            HealthCheck,
        ] = {}

        self._lock = threading.RLock()

        self._logger = logging.getLogger(
            "aurex.production"
        )

        self._configure_logging()

    def _configure_logging(self) -> None:
        """
        Configure production logging once.
        """

        if self._logger.handlers:
            return

        self.config.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        log_file = (
            self.config.log_directory
            / "aurex_runtime.log"
        )

        formatter = logging.Formatter(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(name)s | "
            "%(message)s"
        )

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            formatter
        )

        self._logger.addHandler(
            file_handler
        )

        console_handler = logging.StreamHandler()

        console_handler.setFormatter(
            formatter
        )

        self._logger.addHandler(
            console_handler
        )

        level = getattr(
            logging,
            self.config.log_level,
            logging.INFO,
        )

        self._logger.setLevel(level)

        self._logger.propagate = False

    def start(self) -> None:
        with self._lock:
            self.metrics.started_at = time.time()
            self.metrics.stopped_at = None

            self._logger.info(
                "AUREX production monitor started."
            )

    def stop(self) -> None:
        with self._lock:
            self.metrics.stopped_at = time.time()

            self._logger.info(
                "AUREX production monitor stopped."
            )

    def record_cycle(
        self,
        duration_ms: float,
        success: bool = True,
    ) -> None:
        with self._lock:
            self.metrics.record_cycle(
                duration_ms,
                success,
            )

            if success:
                self._logger.debug(
                    "Runtime cycle completed "
                    "in %.3f ms.",
                    duration_ms,
                )
            else:
                self._logger.error(
                    "Runtime cycle failed "
                    "after %.3f ms.",
                    duration_ms,
                )

    def record_error(
        self,
        message: str,
        exc: Exception | None = None,
    ) -> None:
        with self._lock:
            self.metrics.runtime_errors += 1

            if exc is None:
                self._logger.error(
                    "%s",
                    message,
                )
            else:
                self._logger.exception(
                    "%s",
                    message,
                    exc_info=exc,
                )

    def check(
        self,
        name: str,
        checker,
    ) -> HealthCheck:
        """
        Execute one health check safely.

        The checker may return:
        - True
        - False
        - a string
        - a dictionary containing status/message
        """

        start = time.perf_counter()

        try:
            result = checker()

            duration_ms = (
                time.perf_counter()
                - start
            ) * 1000.0

            status = "healthy"
            message = "OK"

            if isinstance(result, dict):
                status = str(
                    result.get(
                        "status",
                        "healthy",
                    )
                ).lower()

                message = str(
                    result.get(
                        "message",
                        "OK",
                    )
                )

            elif isinstance(result, bool):
                status = (
                    "healthy"
                    if result
                    else "unhealthy"
                )

                message = (
                    "OK"
                    if result
                    else "Check returned False"
                )

            elif isinstance(result, str):
                message = result

            health = HealthCheck(
                name=name,
                status=status,
                message=message,
                duration_ms=duration_ms,
            )

        except Exception as exc:
            duration_ms = (
                time.perf_counter()
                - start
            ) * 1000.0

            health = HealthCheck(
                name=name,
                status="unhealthy",
                message=(
                    f"{type(exc).__name__}: "
                    f"{exc}"
                ),
                duration_ms=duration_ms,
            )

            self._logger.exception(
                "Health check '%s' failed.",
                name,
            )

        with self._lock:
            self._health_checks[name] = health

        return health

    def health_check(
        self,
        name: str,
        checker,
    ) -> dict[str, Any]:
        result = self.check(
            name,
            checker,
        )

        return {
            "name": result.name,
            "status": result.status,
            "message": result.message,
            "duration_ms": result.duration_ms,
            "timestamp": result.timestamp,
            "healthy": result.healthy,
        }

    def system_health(self) -> dict[str, Any]:
        """
        Return the current health state.

        Existing checks are summarized without
        executing arbitrary application modules.
        """

        with self._lock:
            checks = {
                name: {
                    "status": check.status,
                    "message": check.message,
                    "duration_ms": (
                        check.duration_ms
                    ),
                    "timestamp": (
                        check.timestamp
                    ),
                    "healthy": check.healthy,
                }
                for name, check
                in self._health_checks.items()
            }

            healthy_count = sum(
                1
                for check
                in self._health_checks.values()
                if check.healthy
            )

            total_checks = len(
                self._health_checks
            )

            overall = (
                "healthy"
                if (
                    total_checks == 0
                    or healthy_count == total_checks
                )
                else "degraded"
            )

            return {
                "status": overall,
                "healthy_checks": healthy_count,
                "total_checks": total_checks,
                "checks": checks,
            }

    def status(self) -> dict[str, Any]:
        """
        Complete production monitoring snapshot.
        """

        with self._lock:
            return {
                "application": {
                    "name": self.config.app_name,
                    "version": self.config.version,
                    "environment": (
                        self.config.environment
                    ),
                },
                "health": self.system_health(),
                "metrics": self.metrics.snapshot(),
                "timestamp": time.time(),
            }

    def reset_metrics(self) -> None:
        with self._lock:
            started_at = (
                self.metrics.started_at
            )

            self.metrics = RuntimeMetrics(
                started_at=started_at
            )

            self._logger.info(
                "Runtime metrics reset."
            )


def create_production_monitor() -> (
    AUREXProductionMonitor
):
    return AUREXProductionMonitor()