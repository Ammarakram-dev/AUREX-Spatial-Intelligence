from __future__ import annotations

import sys
import time
import importlib
from pathlib import Path


# ============================================================
# PROJECT ROOT
# ============================================================

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


# ============================================================
# MODULES
# ============================================================

MODULES = [
    "core.events",
    "core.engine",
    "core.spatial",
    "core.intelligence",
    "core.security",
    "core.intent",
    "core.emergency",
    "core.actions",
    "core.runtime",
    "vision.camera",
    "vision.human_detector",
    "vision.person_tracker",
    "vision.pose_estimator",
    "gesture",
    "identity",
    "voice",
]


# ============================================================
# SIMPLE CYCLE HANDLER
# ============================================================

def cycle_handler():
    """
    Minimal production-safe handler used to validate
    the runtime orchestration layer.
    """
    return {
        "status": "ok",
        "people_count": 0,
        "object_count": 0,
    }


# ============================================================
# IMPORT TEST
# ============================================================

def test_imports():

    failures = []

    for module_name in MODULES:

        try:
            importlib.import_module(module_name)

        except Exception as exc:

            failures.append(
                f"{module_name}: "
                f"{type(exc).__name__}: {exc}"
            )

    assert not failures, (
        "Import failures:\n"
        + "\n".join(failures)
    )


# ============================================================
# START / STOP
# ============================================================

def test_runtime_start_stop():

    from core.runtime import AUREXRuntime

    runtime = AUREXRuntime()

    runtime.start()

    assert runtime.snapshot.state.value == "running"

    runtime.stop()

    assert runtime.snapshot.state.value == "stopped"


# ============================================================
# RUNTIME CYCLE
# ============================================================

def test_runtime_cycle():

    from core.runtime import AUREXRuntime

    runtime = AUREXRuntime()

    runtime.start()

    result = runtime.execute_cycle(
        cycle_handler
    )

    assert result is not None

    assert runtime.snapshot.cycle_count >= 1

    assert runtime.snapshot.successful_cycles >= 1

    assert runtime.snapshot.failed_cycles == 0

    runtime.stop()


# ============================================================
# PERFORMANCE
# ============================================================

def test_runtime_speed():

    from core.runtime import AUREXRuntime

    runtime = AUREXRuntime()

    runtime.start()

    start = time.perf_counter()

    for _ in range(10):

        runtime.execute_cycle(
            cycle_handler
        )

    elapsed = time.perf_counter() - start

    runtime.stop()

    average_ms = (
        elapsed / 10
    ) * 1000

    print()

    print(
        f"Average runtime cycle: "
        f"{average_ms:.2f} ms"
    )

    assert average_ms < 1000


# ============================================================
# SNAPSHOT
# ============================================================

def test_snapshot_integrity():

    from core.runtime import AUREXRuntime

    runtime = AUREXRuntime()

    runtime.start()

    runtime.execute_cycle(
        cycle_handler
    )

    snapshot = runtime.snapshot

    assert snapshot is not None

    assert snapshot.cycle_count >= 1

    assert snapshot.people_count >= 0

    assert snapshot.object_count >= 0

    assert snapshot.active_modules >= 0

    assert snapshot.failed_modules >= 0

    assert isinstance(
        snapshot.situation,
        str
    )

    assert isinstance(
        snapshot.priority,
        str
    )

    assert isinstance(
        snapshot.security_state,
        str
    )

    runtime.stop()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print()

    print("=" * 60)

    print(
        "AUREX STEP 3 — "
        "SYSTEM INTEGRITY TEST"
    )

    print("=" * 60)

    print()

    print(
        "[1/5] Checking module imports..."
    )

    test_imports()

    print("      PASS")

    print(
        "[2/5] Checking runtime start/stop..."
    )

    test_runtime_start_stop()

    print("      PASS")

    print(
        "[3/5] Checking runtime cycle..."
    )

    test_runtime_cycle()

    print("      PASS")

    print(
        "[4/5] Checking runtime performance..."
    )

    test_runtime_speed()

    print("      PASS")

    print(
        "[5/5] Checking runtime snapshot..."
    )

    test_snapshot_integrity()

    print("      PASS")

    print()

    print("=" * 60)

    print(
        "STEP 3 SYSTEM INTEGRITY "
        "TESTS PASSED"
    )

    print("=" * 60)

    print()