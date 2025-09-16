"""Persistence helpers for the player's long-term research progress."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List

import json


DEFAULT_JOURNAL_PATH = Path.home() / ".mechanistic_mech_journal.json"


@dataclass
class InsightRecord:
    """Represents the player's familiarity with a single concept."""

    title: str
    summary: str
    mastered: bool = False
    tasks_completed: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, object]:
        return {
            "title": self.title,
            "summary": self.summary,
            "mastered": self.mastered,
            "tasks_completed": list(self.tasks_completed),
        }

    @classmethod
    def from_dict(cls, payload: Dict[str, object]) -> "InsightRecord":
        return cls(
            title=str(payload.get("title", "")),
            summary=str(payload.get("summary", "")),
            mastered=bool(payload.get("mastered", False)),
            tasks_completed=list(payload.get("tasks_completed", [])),
        )


@dataclass
class ResearchJournal:
    """Tracks discoveries across sessions and stores them on disk."""

    records: Dict[str, InsightRecord] = field(default_factory=dict)
    path: Path = DEFAULT_JOURNAL_PATH

    @classmethod
    def load(cls, path: Path | None = None) -> "ResearchJournal":
        real_path = path or DEFAULT_JOURNAL_PATH
        try:
            data = json.loads(real_path.read_text())
        except FileNotFoundError:
            return cls(path=real_path)
        except Exception:
            # Corrupt save files should not break the game; start fresh instead.
            return cls(path=real_path)

        records = {
            title: InsightRecord.from_dict(payload) for title, payload in data.items()
        }
        return cls(records=records, path=real_path)

    # ------------------------------------------------------------------
    # Mutation helpers
    # ------------------------------------------------------------------
    def log_insight(self, title: str, summary: str) -> None:
        record = self.records.get(title)
        if record is None:
            self.records[title] = InsightRecord(title=title, summary=summary)
        else:
            if summary and summary != record.summary:
                record.summary = summary

    def mark_task_completed(self, title: str, task_id: str) -> None:
        record = self.records.setdefault(title, InsightRecord(title=title, summary=""))
        if task_id not in record.tasks_completed:
            record.tasks_completed.append(task_id)

    def mark_mastered(self, title: str) -> None:
        record = self.records.setdefault(title, InsightRecord(title=title, summary=""))
        record.mastered = True

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def tasks_for(self, title: str) -> List[str]:
        record = self.records.get(title)
        return list(record.tasks_completed) if record else []

    def is_mastered(self, title: str) -> bool:
        record = self.records.get(title)
        return bool(record and record.mastered)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def save(self) -> None:
        try:
            serialised = {k: v.to_dict() for k, v in self.records.items()}
            self.path.write_text(json.dumps(serialised, indent=2, sort_keys=True))
        except Exception:
            # Ignore file-system errors in headless/testing environments.
            return
