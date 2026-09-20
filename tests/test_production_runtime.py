from core.runtime import (
    AUREXRuntime,
    AUREXIntelligenceBridge,
    RuntimeState,
    ModuleState,
)


def test_runtime_lifecycle():
    runtime = AUREXRuntime()

    runtime.register_module("camera")

    assert runtime.state == RuntimeState.STOPPED
    assert runtime.start() is True
    assert runtime.state == RuntimeState.RUNNING

    assert runtime.pause() is True
    assert runtime.state == RuntimeState.PAUSED

    assert runtime.resume() is True
    assert runtime.state == RuntimeState.RUNNING

    assert runtime.stop() is True
    assert runtime.state == RuntimeState.STOPPED


def test_module_management():
    runtime = AUREXRuntime()

    runtime.register_module("test_module")

    assert "test_module" in runtime.modules
    assert runtime.modules["test_module"].state == ModuleState.READY

    assert runtime.disable_module("test_module") is True
    assert runtime.modules["test_module"].enabled is False

    assert runtime.enable_module("test_module") is True
    assert runtime.modules["test_module"].enabled is True


def test_module_execution():
    runtime = AUREXRuntime()

    def handler(value):
        return value * 2

    runtime.register_module(
        "calculator",
        handler=handler,
    )

    runtime.start()

    result = runtime.execute_module(
        "calculator",
        21,
    )

    assert result == 42
    assert runtime.modules["calculator"].update_count == 1


def test_runtime_cycle():
    runtime = AUREXRuntime()

    runtime.register_module("intelligence")
    runtime.start()

    result = runtime.execute_cycle(
        lambda: {
            "people_count": 2,
            "object_count": 4,
            "situation": "normal_activity",
            "priority": "normal",
            "security_state": "trusted",
        }
    )

    assert result["people_count"] == 2
    assert runtime.cycle_count == 1
    assert runtime.successful_cycles == 1
    assert runtime.snapshot.people_count == 2
    assert runtime.snapshot.object_count == 4


def test_audit():
    runtime = AUREXRuntime()

    runtime.register_module("camera")

    assert len(runtime.audit.records) == 1
    assert runtime.audit.records[0].event == "module_registered"


def test_intelligence_bridge():
    bridge = AUREXIntelligenceBridge()

    result = bridge.process(
        human_states=[
            {
                "person_id": "person_1",
                "movement_distance": 0.15,
                "movement_direction": "forward",
                "zone": "center",
            }
        ]
    )

    assert result.people_count == 1
    assert result.situation.value == "normal_activity"


if __name__ == "__main__":
    test_runtime_lifecycle()
    test_module_management()
    test_module_execution()
    test_runtime_cycle()
    test_audit()
    test_intelligence_bridge()

    print("STEP 2 PRODUCTION RUNTIME TESTS PASSED")