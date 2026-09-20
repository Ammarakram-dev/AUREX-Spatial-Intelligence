from __future__ import annotations

import time
from typing import Any, Dict, Iterable, List, Optional, Set

from .memory_state import (
    MemoryEvent,
    MemoryEventType,
    TemporalMemoryState,
)


class AUREXTemporalMemory:
    """
    Lightweight temporal memory for AUREX.

    Tracks changes between observations rather than storing raw camera
    frames. This keeps the memory layer computationally lightweight.
    """

    def __init__(
        self,
        history_limit: int = 120,
        event_limit: int = 240,
    ):
        self.history_limit = max(1, int(history_limit))
        self.event_limit = max(1, int(event_limit))

        self.frame_index = 0

        self.history: List[TemporalMemoryState] = []
        self.events: List[MemoryEvent] = []

        self.latest: Optional[TemporalMemoryState] = None

    @staticmethod
    def _safe_value(
        obj: Any,
        name: str,
        default: Any = None,
    ) -> Any:
        if obj is None:
            return default

        if isinstance(obj, dict):
            return obj.get(name, default)

        return getattr(obj, name, default)

    @staticmethod
    def _enum_value(
        value: Any,
        default: str = "unknown",
    ) -> str:
        if value is None:
            return default

        if hasattr(value, "value"):
            return str(value.value)

        return str(value).lower()

    def _people_ids(self, human_states: Any) -> Set[str]:
        if human_states is None:
            return set()

        if isinstance(human_states, dict):
            items = human_states.values()
        else:
            try:
                items = list(human_states)
            except TypeError:
                return set()

        result: Set[str] = set()

        for item in items:
            person_id = self._safe_value(
                item,
                "person_id",
                None,
            )

            if person_id is not None:
                result.add(str(person_id))

        return result

    def _object_labels(self, objects: Any) -> Set[str]:
        if objects is None:
            return set()

        if isinstance(objects, dict):
            items = objects.values()
        else:
            try:
                items = list(objects)
            except TypeError:
                return set()

        result: Set[str] = set()

        for item in items:
            label = self._safe_value(
                item,
                "label",
                None,
            )

            if label is not None:
                result.add(str(label).lower())

        return result

    def _environment_state(
        self,
        environment: Any,
    ) -> str:
        if environment is None:
            return "unknown"

        value = self._safe_value(
            environment,
            "state",
            "unknown",
        )

        return self._enum_value(value)

    def _security_state(
        self,
        security: Any,
    ) -> str:
        if security is None:
            return "unknown"

        return self._enum_value(
            self._safe_value(
                security,
                "state",
                "unknown",
            )
        )

    def _security_level(
        self,
        security: Any,
    ) -> str:
        if security is None:
            return "low"

        return self._enum_value(
            self._safe_value(
                security,
                "level",
                "low",
            ),
            "low",
        )

    def _hazard_count(
        self,
        hazards: Any,
    ) -> int:
        if hazards is None:
            return 0

        if isinstance(hazards, dict):
            return len(hazards)

        try:
            return len(hazards)
        except TypeError:
            return 1

    def _behavior_count(
        self,
        behavior: Any,
    ) -> int:
        if behavior is None:
            return 0

        anomalies = self._safe_value(
            behavior,
            "anomalies",
            [],
        )

        try:
            return len(anomalies)
        except TypeError:
            return 0

    def _intent(
        self,
        intent: Any,
        field: str,
    ) -> str:
        if intent is None:
            return "unknown"

        value = self._safe_value(
            intent,
            field,
            "unknown",
        )

        if hasattr(value, "value"):
            return str(value.value)

        return str(value).lower()

    def _create_event(
        self,
        event_type: MemoryEventType,
        description: str,
        confidence: float,
        timestamp: float,
        entity_id: str | None = None,
        previous_value: Any = None,
        current_value: Any = None,
        metadata: Dict[str, Any] | None = None,
    ) -> MemoryEvent:
        event = MemoryEvent(
            event_type=event_type,
            description=description,
            confidence=confidence,
            timestamp=timestamp,
            entity_id=entity_id,
            previous_value=previous_value,
            current_value=current_value,
            metadata=metadata or {},
        )

        self.events.append(event)

        if len(self.events) > self.event_limit:
            self.events = self.events[-self.event_limit :]

        return event

    def _compare_sets(
        self,
        previous: Set[str],
        current: Set[str],
        added_type: MemoryEventType,
        removed_type: MemoryEventType,
        entity_name: str,
        timestamp: float,
    ) -> List[MemoryEvent]:
        generated: List[MemoryEvent] = []

        added = current - previous
        removed = previous - current

        for entity_id in sorted(added):
            generated.append(
                self._create_event(
                    added_type,
                    f"{entity_name} '{entity_id}' entered the observed state.",
                    0.90,
                    timestamp,
                    entity_id=entity_id,
                    current_value=entity_id,
                )
            )

        for entity_id in sorted(removed):
            generated.append(
                self._create_event(
                    removed_type,
                    f"{entity_name} '{entity_id}' left the observed state.",
                    0.90,
                    timestamp,
                    entity_id=entity_id,
                    previous_value=entity_id,
                )
            )

        return generated

    def _compare_scalar(
        self,
        previous: str,
        current: str,
        event_type: MemoryEventType,
        description_prefix: str,
        timestamp: float,
        confidence: float = 0.85,
    ) -> Optional[MemoryEvent]:
        if previous == current:
            return None

        return self._create_event(
            event_type,
            f"{description_prefix}: {previous} -> {current}",
            confidence,
            timestamp,
            previous_value=previous,
            current_value=current,
        )

    def observe(
        self,
        human_states: Any = None,
        objects: Any = None,
        environment: Any = None,
        security: Any = None,
        hazards: Any = None,
        behavior: Any = None,
        voice_command: Any = None,
        multimodal_intent: Any = None,
        timestamp: float | None = None,
    ) -> TemporalMemoryState:
        now = time.time() if timestamp is None else float(timestamp)

        current_people = self._people_ids(human_states)
        current_objects = self._object_labels(objects)

        current_environment = self._environment_state(environment)
        current_security = self._security_state(security)
        current_security_level = self._security_level(security)

        current_hazards = self._hazard_count(hazards)
        current_behavior = self._behavior_count(behavior)

        current_voice = self._intent(
            voice_command,
            "intent",
        )

        current_multimodal = self._intent(
            multimodal_intent,
            "intent",
        )

        if current_multimodal == "unknown":
            current_multimodal = self._intent(
                multimodal_intent,
                "primary",
            )

        previous = self.latest

        state = TemporalMemoryState(
            frame_index=self.frame_index,
            timestamp=now,
            people_ids=sorted(current_people),
            object_labels=sorted(current_objects),
            environment_state=current_environment,
            security_state=current_security,
            security_level=current_security_level,
            hazard_count=current_hazards,
            behavior_anomaly_count=current_behavior,
            voice_intent=current_voice,
            multimodal_intent=current_multimodal,
        )

        if previous is not None:
            previous_people = set(previous.people_ids)
            previous_objects = set(previous.object_labels)

            state.events.extend(
                self._compare_sets(
                    previous_people,
                    current_people,
                    MemoryEventType.PERSON_ENTERED,
                    MemoryEventType.PERSON_LEFT,
                    "Person",
                    now,
                )
            )

            state.events.extend(
                self._compare_sets(
                    previous_objects,
                    current_objects,
                    MemoryEventType.OBJECT_APPEARED,
                    MemoryEventType.OBJECT_DISAPPEARED,
                    "Object",
                    now,
                )
            )

            event = self._compare_scalar(
                previous.environment_state,
                current_environment,
                MemoryEventType.STATE_CHANGED,
                "Environment state changed",
                now,
            )

            if event:
                state.events.append(event)

            event = self._compare_scalar(
                previous.security_state,
                current_security,
                MemoryEventType.SECURITY_CHANGED,
                "Security state changed",
                now,
            )

            if event:
                state.events.append(event)

            event = self._compare_scalar(
                previous.voice_intent,
                current_voice,
                MemoryEventType.INTENT_CHANGED,
                "Voice intent changed",
                now,
            )

            if event:
                state.events.append(event)

            event = self._compare_scalar(
                previous.multimodal_intent,
                current_multimodal,
                MemoryEventType.INTENT_CHANGED,
                "Multimodal intent changed",
                now,
            )

            if event:
                state.events.append(event)

            if previous.hazard_count == 0 and current_hazards > 0:
                state.events.append(
                    self._create_event(
                        MemoryEventType.HAZARD_STARTED,
                        "Hazard activity started.",
                        0.90,
                        now,
                        previous_value=0,
                        current_value=current_hazards,
                    )
                )

            elif previous.hazard_count > 0 and current_hazards == 0:
                state.events.append(
                    self._create_event(
                        MemoryEventType.HAZARD_CLEARED,
                        "Hazard activity cleared.",
                        0.85,
                        now,
                        previous_value=previous.hazard_count,
                        current_value=0,
                    )
                )

            if (
                previous.behavior_anomaly_count == 0
                and current_behavior > 0
            ):
                state.events.append(
                    self._create_event(
                        MemoryEventType.BEHAVIOR_CHANGED,
                        "Observable behavior anomaly activity started.",
                        0.80,
                        now,
                        previous_value=0,
                        current_value=current_behavior,
                    )
                )

        self.frame_index += 1

        self.history.append(state)

        if len(self.history) > self.history_limit:
            self.history = self.history[-self.history_limit :]

        self.latest = state

        return state

    def recent_events(
        self,
        limit: int = 20,
    ) -> List[MemoryEvent]:
        limit = max(1, int(limit))
        return self.events[-limit:]

    def recent_states(
        self,
        limit: int = 20,
    ) -> List[TemporalMemoryState]:
        limit = max(1, int(limit))
        return self.history[-limit:]

    def state_duration(
        self,
        state: str,
    ) -> int:
        if not self.history:
            return 0

        target = str(state).lower()
        count = 0

        for item in reversed(self.history):
            if item.environment_state != target:
                break

            count += 1

        return count

    def has_recent_event(
        self,
        event_type: MemoryEventType,
        limit: int = 20,
    ) -> bool:
        for event in self.recent_events(limit):
            if event.event_type == event_type:
                return True

        return False

    def reset(self) -> None:
        self.frame_index = 0
        self.history.clear()
        self.events.clear()
        self.latest = None

    def status(self) -> Dict[str, Any]:
        return {
            "frame_index": self.frame_index,
            "history_length": len(self.history),
            "event_count": len(self.events),
            "latest": self.latest.to_dict()
            if self.latest
            else None,
            "recent_events": [
                event.to_dict()
                for event in self.recent_events(10)
            ],
        }