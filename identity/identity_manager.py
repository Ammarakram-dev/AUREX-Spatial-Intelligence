"""
AUREX Spatial Intelligence
Face Identity Manager
Phase 23
"""

from dataclasses import dataclass
from typing import Optional

from .face_database import AUREXFaceDatabase
from .face_embedding import AUREXFaceEmbedding


@dataclass
class IdentityMatch:

    identity: Optional[str]
    confidence: float
    matched: bool


class AUREXIdentityManager:

    def __init__(
        self,
        database: Optional[
            AUREXFaceDatabase
        ] = None,
        matcher: Optional[
            AUREXFaceEmbedding
        ] = None,
        threshold: float = 0.90,
    ) -> None:

        self.database = (
            database
            or AUREXFaceDatabase()
        )

        self.matcher = (
            matcher
            or AUREXFaceEmbedding()
        )

        self.threshold = threshold

    def enroll(
        self,
        identity: str,
        landmarks,
    ) -> bool:

        embedding = (
            self.matcher.create(
                landmarks
            )
        )

        if not embedding:
            return False

        self.database.enroll(
            identity,
            embedding,
        )

        return True

    def match(
        self,
        landmarks,
    ) -> IdentityMatch:

        embedding = (
            self.matcher.create(
                landmarks
            )
        )

        if not embedding:
            return IdentityMatch(
                identity=None,
                confidence=0.0,
                matched=False,
            )

        best_identity = None
        best_confidence = 0.0

        for identity, profile in (
            self.database.all().items()
        ):

            stored = profile.get(
                "embedding"
            )

            if not stored:
                continue

            confidence = (
                self.matcher.similarity(
                    embedding,
                    stored,
                )
            )

            if confidence > best_confidence:

                best_confidence = (
                    confidence
                )

                best_identity = identity

        matched = (
            best_identity is not None
            and best_confidence
            >= self.threshold
        )

        if not matched:
            best_identity = None

        return IdentityMatch(
            identity=best_identity,
            confidence=best_confidence,
            matched=matched,
        )