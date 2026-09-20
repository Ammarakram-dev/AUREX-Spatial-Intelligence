"""
AUREX Spatial Intelligence
Local Face Identity Database
Phase 23
"""

import json
from pathlib import Path
from typing import Dict, Optional


class AUREXFaceDatabase:

    def __init__(
        self,
        path: str = "data/identity/identities.json",
    ) -> None:

        self.path = Path(path)
        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.identities: Dict[str, dict] = {}

        self.load()

    def load(self) -> None:

        if not self.path.exists():
            self.identities = {}
            return

        try:

            with self.path.open(
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            if isinstance(data, dict):
                self.identities = data
            else:
                self.identities = {}

        except (
            json.JSONDecodeError,
            OSError,
        ):

            self.identities = {}

    def save(self) -> None:

        with self.path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self.identities,
                file,
                indent=2,
            )

    def enroll(
        self,
        identity: str,
        embedding,
    ) -> None:

        self.identities[identity] = {
            "embedding": embedding,
        }

        self.save()

    def get(
        self,
        identity: str,
    ) -> Optional[dict]:

        return self.identities.get(
            identity
        )

    def all(self) -> Dict[str, dict]:

        return dict(
            self.identities
        )

    def remove(
        self,
        identity: str,
    ) -> bool:

        if identity not in self.identities:
            return False

        del self.identities[identity]

        self.save()

        return True

    def clear(self) -> None:

        self.identities = {}

        self.save()