from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def cycle_handler():
    return {
        "status": "ok",
        "people_count": 0,
        "object_count": 0,
    }


def main():
    from core.runtime import AUREXRuntime

    print()
    print("=" * 72)
    print("AUREX STEP 3 — PERFORMANCE VALIDATION")
    print("=" * 72)
    print()

    runtime = AUREXRuntime()

    print("[1/5] Starting runtime...")
    runtime.start()

    assert runtime.snapshot.state.value == "running"
    print("      PASS")

    print("[2/5] Warm-up cycles...")
    for _ in range(10):
        runtime.execute_cycle(cycle_handler)

    print("      PASS")

    print("[3/5] Running performance benchmark...")

    iterations = 100

    start = time.perf_counter()

    for _ in range(iterations):
        result = runtime.execute_cycle(cycle_handler)
        assert result is not None

    elapsed = time.perf_counter() - start

    average_ms = (elapsed / iterations) * 1000
    cycles_per_second = (
        iterations / elapsed
        if elapsed > 0
        else 0
    )

    print("      PASS")

    print("[4/5] Checking runtime statistics...")

    snapshot = runtime.snapshot

    assert snapshot.cycle_count >= iterations + 10
    assert snapshot.successful_cycles >= iterations + 10
    assert snapshot.failed_cycles == 0
    assert snapshot.cycle_time_ms >= 0
    assert snapshot.average_cycle_time_ms >= 0

    print("      PASS")

    print("[5/5] Stopping runtime...")

    runtime.stop()

    assert runtime.snapshot.state.value == "stopped"

    print("      PASS")

    print()
    print("-" * 72)
    print("PERFORMANCE RESULTS")
    print("-" * 72)
    print()
    print(f"Benchmark cycles ........ {iterations}")
    print(f"Total benchmark time .... {elapsed:.4f} sec")
    print(f"Average cycle ........... {average_ms:.3f} ms")
    print(f"Cycles per second ....... {cycles_per_second:.2f}")
    print(
        f"Runtime total cycles .... "
        f"{snapshot.cycle_count}"
    )
    print(
        f"Successful cycles ....... "
        f"{snapshot.successful_cycles}"
    )
    print(
        f"Failed cycles ........... "
        f"{snapshot.failed_cycles}"
    )
    print()

    if snapshot.failed_cycles != 0:
        print("=" * 72)
        print("PERFORMANCE VALIDATION FAILED")
        print("=" * 72)
        return 1

    print("=" * 72)
    print("STEP 3 PERFORMANCE VALIDATION PASSED")
    print("=" * 72)
    print()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())