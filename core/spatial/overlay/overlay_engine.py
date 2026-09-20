from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from .overlay_state import (
    OverlayAnchor,
    OverlayType,
    RealityOverlay,
)


class AUREXRealityOverlay:

    def __init__(
        self,
        minimum_confidence: float = 0.45,
        history_limit: int = 30,
    ) -> None:

        self.minimum_confidence = minimum_confidence
        self.history_limit = history_limit
        self.history: List[List[RealityOverlay]] = []

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    @staticmethod
    def _confidence(value: Any) -> float:
        try:
            return max(
                0.0,
                min(1.0, float(value)),
            )
        except (TypeError, ValueError):
            return 0.0

    @staticmethod
    def _center_from_person(person):
        center = getattr(
            person,
            "current_center",
            None,
        )

        if center is not None:
            return float(center[0]), float(center[1])

        x1 = float(getattr(person, "x1", 0.0))
        y1 = float(getattr(person, "y1", 0.0))
        x2 = float(getattr(person, "x2", 0.0))
        y2 = float(getattr(person, "y2", 0.0))

        return (
            (x1 + x2) / 2.0,
            (y1 + y2) / 2.0,
        )

    @staticmethod
    def _bbox_from_person(person):
        return (
            float(getattr(person, "x1", 0.0)),
            float(getattr(person, "y1", 0.0)),
            float(getattr(person, "x2", 0.0)),
            float(getattr(person, "y2", 0.0)),
        )

    # ---------------------------------------------------------
    # Person overlays
    # ---------------------------------------------------------

    def people_overlays(
        self,
        people: Optional[Iterable[Any]] = None,
    ) -> List[RealityOverlay]:

        overlays = []

        for person in people or []:

            x1, y1, x2, y2 = self._bbox_from_person(
                person
            )

            confidence = self._confidence(
                getattr(
                    person,
                    "confidence",
                    1.0,
                )
            )

            if confidence < self.minimum_confidence:
                continue

            person_id = str(
                getattr(
                    person,
                    "person_id",
                    "person",
                )
            )

            direction = str(
                getattr(
                    person,
                    "movement_direction",
                    "stationary",
                )
            )

            overlays.append(
                RealityOverlay(
                    overlay_id=f"person:{person_id}",
                    overlay_type=OverlayType.PERSON,
                    label=f"PERSON {person_id}",
                    confidence=confidence,
                    anchor=OverlayAnchor(
                        x=x1,
                        y=y1,
                        width=x2 - x1,
                        height=y2 - y1,
                    ),
                    priority=30,
                    metadata={
                        "person_id": person_id,
                        "movement_direction": direction,
                        "zone": getattr(
                            person,
                            "zone",
                            None,
                        ),
                    },
                )
            )

        return overlays

    # ---------------------------------------------------------
    # Scene object overlays
    # ---------------------------------------------------------

    def object_overlays(
        self,
        objects: Optional[Iterable[Any]] = None,
    ) -> List[RealityOverlay]:

        overlays = []

        for obj in objects or []:

            bbox = getattr(
                obj,
                "bbox",
                None,
            )

            if bbox is None:
                continue

            x1, y1, x2, y2 = bbox

            confidence = self._confidence(
                getattr(
                    obj,
                    "confidence",
                    1.0,
                )
            )

            if confidence < self.minimum_confidence:
                continue

            object_id = str(
                getattr(
                    obj,
                    "object_id",
                    "object",
                )
            )

            label = str(
                getattr(
                    obj,
                    "label",
                    "object",
                )
            )

            overlays.append(
                RealityOverlay(
                    overlay_id=f"object:{object_id}",
                    overlay_type=OverlayType.OBJECT,
                    label=label.upper(),
                    confidence=confidence,
                    anchor=OverlayAnchor(
                        x=float(x1),
                        y=float(y1),
                        width=float(x2 - x1),
                        height=float(y2 - y1),
                    ),
                    priority=20,
                    metadata={
                        "object_id": object_id,
                        "class_id": getattr(
                            obj,
                            "class_id",
                            None,
                        ),
                    },
                )
            )

        return overlays

    # ---------------------------------------------------------
    # Relationship overlays
    # ---------------------------------------------------------

    def relationship_overlays(
        self,
        relationships: Optional[Iterable[Any]] = None,
        people: Optional[Iterable[Any]] = None,
    ) -> List[RealityOverlay]:

        overlays = []

        people_by_id = {
            str(
                getattr(
                    person,
                    "person_id",
                    "",
                )
            ): person
            for person in people or []
        }

        for index, relationship in enumerate(
            relationships or []
        ):

            source_id = str(
                getattr(
                    relationship,
                    "source_id",
                    "",
                )
            )

            target_id = str(
                getattr(
                    relationship,
                    "target_id",
                    "",
                )
            )

            source = people_by_id.get(source_id)
            target = people_by_id.get(target_id)

            if source is None or target is None:
                continue

            sx, sy = self._center_from_person(source)
            tx, ty = self._center_from_person(target)

            confidence = self._confidence(
                getattr(
                    relationship,
                    "confidence",
                    0.0,
                )
            )

            if confidence < self.minimum_confidence:
                continue

            relationship_name = str(
                getattr(
                    relationship,
                    "relationship",
                    "relationship",
                )
            )

            overlays.append(
                RealityOverlay(
                    overlay_id=f"relationship:{index}",
                    overlay_type=OverlayType.RELATIONSHIP,
                    label=relationship_name.upper(),
                    confidence=confidence,
                    anchor=OverlayAnchor(
                        x=(sx + tx) / 2.0,
                        y=(sy + ty) / 2.0,
                    ),
                    priority=40,
                    metadata={
                        "source_id": source_id,
                        "target_id": target_id,
                        "source_center": [
                            sx,
                            sy,
                        ],
                        "target_center": [
                            tx,
                            ty,
                        ],
                    },
                )
            )

        return overlays

    # ---------------------------------------------------------
    # Context overlay
    # ---------------------------------------------------------

    def context_overlay(
        self,
        context: Optional[Any] = None,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> List[RealityOverlay]:

        if context is None:
            return []

        context_type = getattr(
            context,
            "context_type",
            None,
        )

        if context_type is None:
            return []

        confidence = self._confidence(
            getattr(
                context,
                "confidence",
                0.0,
            )
        )

        if confidence < self.minimum_confidence:
            return []

        value = getattr(
            context_type,
            "value",
            str(context_type),
        )

        return [
            RealityOverlay(
                overlay_id="context:global",
                overlay_type=OverlayType.CONTEXT,
                label=str(value).replace(
                    "_",
                    " ",
                ).upper(),
                confidence=confidence,
                anchor=OverlayAnchor(
                    x=frame_width * 0.02,
                    y=frame_height * 0.88,
                ),
                priority=60,
                metadata={
                    "people_count": getattr(
                        context,
                        "people_count",
                        0,
                    ),
                },
            )
        ]

    # ---------------------------------------------------------
    # Hazard overlay
    # ---------------------------------------------------------

    def hazard_overlays(
        self,
        hazards: Optional[Iterable[Any]] = None,
        people: Optional[Iterable[Any]] = None,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> List[RealityOverlay]:

        overlays = []

        people_by_id = {
            str(
                getattr(
                    person,
                    "person_id",
                    "",
                )
            ): person
            for person in people or []
        }

        for index, hazard in enumerate(
            hazards or []
        ):

            confidence = self._confidence(
                getattr(
                    hazard,
                    "confidence",
                    0.0,
                )
            )

            if confidence < self.minimum_confidence:
                continue

            hazard_type = getattr(
                hazard,
                "hazard_type",
                "hazard",
            )

            label = getattr(
                hazard_type,
                "value",
                str(hazard_type),
            )

            person_ids = getattr(
                hazard,
                "person_ids",
                [],
            )

            anchor_x = frame_width * 0.50
            anchor_y = frame_height * 0.08

            if person_ids:
                person = people_by_id.get(
                    str(person_ids[0])
                )

                if person is not None:
                    anchor_x, anchor_y = (
                        self._center_from_person(
                            person
                        )
                    )

            overlays.append(
                RealityOverlay(
                    overlay_id=f"hazard:{index}",
                    overlay_type=OverlayType.HAZARD,
                    label=(
                        "HAZARD: "
                        + str(label).replace(
                            "_",
                            " ",
                        ).upper()
                    ),
                    confidence=confidence,
                    anchor=OverlayAnchor(
                        x=anchor_x,
                        y=anchor_y,
                    ),
                    priority=100,
                    metadata={
                        "severity": getattr(
                            getattr(
                                hazard,
                                "severity",
                                None,
                            ),
                            "value",
                            str(
                                getattr(
                                    hazard,
                                    "severity",
                                    "",
                                )
                            ),
                        ),
                        "person_ids": list(
                            person_ids
                        ),
                    },
                )
            )

        return overlays

    # ---------------------------------------------------------
    # Full overlay composition
    # ---------------------------------------------------------

    def build(
        self,
        people: Optional[Iterable[Any]] = None,
        objects: Optional[Iterable[Any]] = None,
        relationships: Optional[Iterable[Any]] = None,
        context: Optional[Any] = None,
        hazards: Optional[Iterable[Any]] = None,
        frame_width: int = 640,
        frame_height: int = 480,
    ) -> List[RealityOverlay]:

        overlays = []

        overlays.extend(
            self.people_overlays(people)
        )

        overlays.extend(
            self.object_overlays(objects)
        )

        overlays.extend(
            self.relationship_overlays(
                relationships,
                people,
            )
        )

        overlays.extend(
            self.context_overlay(
                context,
                frame_width,
                frame_height,
            )
        )

        overlays.extend(
            self.hazard_overlays(
                hazards,
                people,
                frame_width,
                frame_height,
            )
        )

        overlays.sort(
            key=lambda item: item.priority,
            reverse=True,
        )

        self.history.append(overlays)

        if len(self.history) > self.history_limit:
            self.history = self.history[
                -self.history_limit:
            ]

        return overlays

    def reset(self) -> None:
        self.history.clear()

    def status(self) -> Dict[str, Any]:
        return {
            "history_size": len(self.history),
            "minimum_confidence": (
                self.minimum_confidence
            ),
            "latest_overlay_count": (
                len(self.history[-1])
                if self.history
                else 0
            ),
        }