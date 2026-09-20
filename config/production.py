from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return int(value)
    except ValueError:
        return default


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)

    if value is None:
        return default

    try:
        return float(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class ProductionConfig:
    """
    Central production configuration for AUREX.

    Values can be overridden through environment variables.
    """

    app_name: str = os.getenv(
        "AUREX_APP_NAME",
        "AUREX Spatial Intelligence",
    )

    environment: str = os.getenv(
        "AUREX_ENVIRONMENT",
        "production",
    )

    version: str = os.getenv(
        "AUREX_VERSION",
        "1.0.0",
    )

    host: str = os.getenv(
        "AUREX_HOST",
        "127.0.0.1",
    )

    port: int = _env_int(
        "AUREX_PORT",
        8000,
    )

    debug: bool = _env_bool(
        "AUREX_DEBUG",
        False,
    )

    camera_index: int = _env_int(
        "AUREX_CAMERA_INDEX",
        0,
    )

    camera_width: int = _env_int(
        "AUREX_CAMERA_WIDTH",
        640,
    )

    camera_height: int = _env_int(
        "AUREX_CAMERA_HEIGHT",
        480,
    )

    target_fps: float = _env_float(
        "AUREX_TARGET_FPS",
        30.0,
    )

    log_level: str = os.getenv(
        "AUREX_LOG_LEVEL",
        "INFO",
    ).upper()

    log_directory: Path = Path(
        os.getenv(
            "AUREX_LOG_DIRECTORY",
            str(ROOT_DIR / "logs"),
        )
    )

    data_directory: Path = Path(
        os.getenv(
            "AUREX_DATA_DIRECTORY",
            str(ROOT_DIR / "data"),
        )
    )

    model_directory: Path = Path(
        os.getenv(
            "AUREX_MODEL_DIRECTORY",
            str(ROOT_DIR / "models"),
        )
    )

    audit_enabled: bool = _env_bool(
        "AUREX_AUDIT_ENABLED",
        True,
    )

    metrics_enabled: bool = _env_bool(
        "AUREX_METRICS_ENABLED",
        True,
    )

    voice_enabled: bool = _env_bool(
        "AUREX_VOICE_ENABLED",
        True,
    )

    security_enabled: bool = _env_bool(
        "AUREX_SECURITY_ENABLED",
        True,
    )

    emergency_enabled: bool = _env_bool(
        "AUREX_EMERGENCY_ENABLED",
        True,
    )

    require_confirmation_for_actions: bool = _env_bool(
        "AUREX_REQUIRE_ACTION_CONFIRMATION",
        True,
    )

    max_runtime_errors: int = _env_int(
        "AUREX_MAX_RUNTIME_ERRORS",
        5,
    )

    shutdown_timeout_seconds: float = _env_float(
        "AUREX_SHUTDOWN_TIMEOUT",
        5.0,
    )

    def prepare_directories(self) -> None:
        """
        Create directories required by the production runtime.
        """

        self.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.data_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def validate(self) -> None:
        """
        Validate production configuration.

        Raises:
            ValueError: when a configuration value is invalid.
        """

        if not self.app_name.strip():
            raise ValueError(
                "AUREX_APP_NAME cannot be empty."
            )

        if not self.environment.strip():
            raise ValueError(
                "AUREX_ENVIRONMENT cannot be empty."
            )

        if self.port < 1 or self.port > 65535:
            raise ValueError(
                "AUREX_PORT must be between 1 and 65535."
            )

        if self.camera_index < 0:
            raise ValueError(
                "AUREX_CAMERA_INDEX cannot be negative."
            )

        if self.camera_width <= 0:
            raise ValueError(
                "AUREX_CAMERA_WIDTH must be greater than zero."
            )

        if self.camera_height <= 0:
            raise ValueError(
                "AUREX_CAMERA_HEIGHT must be greater than zero."
            )

        if self.target_fps <= 0:
            raise ValueError(
                "AUREX_TARGET_FPS must be greater than zero."
            )

        if self.max_runtime_errors < 1:
            raise ValueError(
                "AUREX_MAX_RUNTIME_ERRORS must be at least 1."
            )

        if self.shutdown_timeout_seconds <= 0:
            raise ValueError(
                "AUREX_SHUTDOWN_TIMEOUT must be greater than zero."
            )

        allowed_levels = {
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        }

        if self.log_level not in allowed_levels:
            raise ValueError(
                "AUREX_LOG_LEVEL must be one of: "
                + ", ".join(sorted(allowed_levels))
            )

    def summary(self) -> dict:
        """
        Return a safe configuration summary.

        Sensitive environment values are intentionally
        excluded from this output.
        """

        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "version": self.version,
            "host": self.host,
            "port": self.port,
            "debug": self.debug,
            "camera_index": self.camera_index,
            "camera_width": self.camera_width,
            "camera_height": self.camera_height,
            "target_fps": self.target_fps,
            "log_level": self.log_level,
            "audit_enabled": self.audit_enabled,
            "metrics_enabled": self.metrics_enabled,
            "voice_enabled": self.voice_enabled,
            "security_enabled": self.security_enabled,
            "emergency_enabled": self.emergency_enabled,
            "require_confirmation_for_actions": (
                self.require_confirmation_for_actions
            ),
            "max_runtime_errors": self.max_runtime_errors,
            "shutdown_timeout_seconds": (
                self.shutdown_timeout_seconds
            ),
        }


production_config = ProductionConfig()