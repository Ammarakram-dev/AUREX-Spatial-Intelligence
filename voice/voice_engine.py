from __future__ import annotations

import re
from typing import Dict, List, Tuple

from .voice_state import (
    VoiceCommand,
    VoiceIntent,
)


class AUREXVoiceEngine:

    def __init__(
        self,
        minimum_confidence: float = 0.55,
    ) -> None:

        self.minimum_confidence = (
            minimum_confidence
        )

        self.history: List[VoiceCommand] = []

    # ---------------------------------------------------------
    # Normalization
    # ---------------------------------------------------------

    @staticmethod
    def _normalize(text: str) -> str:

        text = text.lower().strip()

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text

    # ---------------------------------------------------------
    # Intent detection
    # ---------------------------------------------------------

    def parse(
        self,
        text: str,
    ) -> VoiceCommand:

        normalized = self._normalize(text)

        if not normalized:

            command = VoiceCommand(
                text=text,
                intent=VoiceIntent.UNKNOWN,
                confidence=0.0,
            )

            self.history.append(command)

            return command

        rules: List[
            Tuple[
                VoiceIntent,
                List[str],
                float,
            ]
        ] = [

            (
                VoiceIntent.EMERGENCY,
                [
                    "emergency",
                    "call emergency",
                    "send emergency",
                    "help me now",
                ],
                0.95,
            ),

            (
                VoiceIntent.HELP,
                [
                    "help",
                    "i need help",
                    "request help",
                    "assist me",
                ],
                0.88,
            ),

            (
                VoiceIntent.LOCK,
                [
                    "lock",
                    "lock system",
                    "secure system",
                    "activate lock",
                ],
                0.90,
            ),

            (
                VoiceIntent.UNLOCK,
                [
                    "unlock",
                    "open security",
                    "disable lock",
                ],
                0.90,
            ),

            (
                VoiceIntent.STOP,
                [
                    "stop",
                    "stop action",
                    "cancel",
                    "abort",
                ],
                0.90,
            ),

            (
                VoiceIntent.CLEAR,
                [
                    "clear",
                    "clear canvas",
                    "erase",
                    "remove drawing",
                ],
                0.88,
            ),

            (
                VoiceIntent.DRAW,
                [
                    "draw",
                    "start drawing",
                    "air draw",
                    "create drawing",
                ],
                0.86,
            ),

            (
                VoiceIntent.SELECT,
                [
                    "select",
                    "choose",
                    "pick",
                ],
                0.78,
            ),

            (
                VoiceIntent.SHOW,
                [
                    "show",
                    "display",
                    "show me",
                    "visualize",
                ],
                0.80,
            ),

            (
                VoiceIntent.HIDE,
                [
                    "hide",
                    "remove overlay",
                    "hide overlay",
                ],
                0.80,
            ),

            (
                VoiceIntent.OBSERVE,
                [
                    "look",
                    "observe",
                    "analyze",
                    "scan",
                    "inspect",
                ],
                0.78,
            ),

            (
                VoiceIntent.STATUS,
                [
                    "status",
                    "system status",
                    "what is happening",
                    "what do you see",
                ],
                0.82,
            ),
        ]

        best_intent = VoiceIntent.UNKNOWN
        best_confidence = 0.0

        for intent, phrases, confidence in rules:

            for phrase in phrases:

                if phrase in normalized:

                    if confidence > best_confidence:

                        best_intent = intent
                        best_confidence = confidence

        entities = self._extract_entities(
            normalized
        )

        command = VoiceCommand(
            text=text,
            intent=best_intent,
            confidence=best_confidence,
            entities=entities,
        )

        self.history.append(command)

        return command

    # ---------------------------------------------------------
    # Entity extraction
    # ---------------------------------------------------------

    @staticmethod
    def _extract_entities(
        text: str,
    ) -> Dict[str, str]:

        entities: Dict[str, str] = {}

        object_words = [
            "person",
            "phone",
            "chair",
            "bottle",
            "laptop",
            "book",
            "table",
            "car",
        ]

        for word in object_words:

            if word in text:

                entities["object"] = word
                break

        zones = [
            "left",
            "right",
            "center",
            "front",
            "back",
            "near",
            "far",
        ]

        for zone in zones:

            if zone in text:

                entities["location"] = zone
                break

        return entities

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def status(self) -> Dict:

        latest = (
            self.history[-1].to_dict()
            if self.history
            else None
        )

        return {
            "history_size": len(
                self.history
            ),
            "latest": latest,
            "minimum_confidence": (
                self.minimum_confidence
            ),
        }

    def reset(self) -> None:
        self.history.clear()