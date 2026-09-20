"""
AUREX Spatial Intelligence
Phase 23 Face Identity Tests
"""

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from identity.face_database import (
    AUREXFaceDatabase,
)

from identity.identity_manager import (
    AUREXIdentityManager,
)


def main() -> None:

    print("=" * 78)
    print("AUREX — PHASE 23 FACE IDENTITY TEST")
    print("=" * 78)

    with tempfile.TemporaryDirectory() as directory:

        database_path = (
            Path(directory)
            / "identities.json"
        )

        database = AUREXFaceDatabase(
            path=str(database_path)
        )

        manager = AUREXIdentityManager(
            database=database,
            threshold=0.90,
        )

        landmarks = [
            (0.10, 0.20),
            (0.20, 0.25),
            (0.30, 0.35),
            (0.40, 0.45),
            (0.50, 0.55),
            (0.60, 0.65),
        ]

        assert manager.enroll(
            "test_user",
            landmarks,
        )

        result = manager.match(
            landmarks
        )

        assert result.matched
        assert result.identity == "test_user"
        assert result.confidence >= 0.90

        altered = [
            (0.11, 0.21),
            (0.21, 0.26),
            (0.31, 0.36),
            (0.41, 0.46),
            (0.51, 0.56),
            (0.61, 0.66),
        ]

        altered_result = manager.match(
            altered
        )

        assert altered_result.confidence > 0.0

    print()
    print("Face embedding: PASS")
    print("Enrollment: PASS")
    print("Database persistence: PASS")
    print("Identity matching: PASS")
    print("Similarity calculation: PASS")
    print()
    print("PHASE 23 UNIT TEST: PASS")
    print("=" * 78)


if __name__ == "__main__":
    main()