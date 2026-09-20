from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


@dataclass
class AuditRecord:
    timestamp: float
    event: str
    source: str
    severity: str = "info"
    message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "event": self.event,
            "source": self.source,
            "severity": self.severity,
            "message": self.message,
            "metadata": self.metadata,
        }


class AUREXAuditLogger:
    def __init__(self, history_limit: int = 500):
        self.history_limit = history_limit
        self.records: List[AuditRecord] = []

    def record(
        self,
        event: str,
        source: str,
        severity: str = "info",
        message: str = "",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditRecord:

        record = AuditRecord(
            timestamp=time.time(),
            event=event,
            source=source,
            severity=severity,
            message=message,
            metadata=metadata or {},
        )

        self.records.append(record)

        if len(self.records) > self.history_limit:
            self.records = self.records[-self.history_limit:]

        return record

    def recent(self, limit: int = 20) -> List[AuditRecord]:
        return self.records[-max(1, limit):]

    def clear(self) -> None:
        self.records.clear()

    def status(self) -> Dict[str, Any]:
        return {
            "record_count": len(self.records),
            "history_limit": self.history_limit,
        }