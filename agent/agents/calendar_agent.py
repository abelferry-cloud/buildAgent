"""Calendar Agent - handles calendar and日程 management."""

from datetime import datetime
from typing import Optional
import json
from pathlib import Path


class CalendarAgent:
    """Agent specialized in calendar and scheduling."""

    def __init__(self, storage_file: str = ".agent/calendar.json"):
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_events()

    def _load_events(self):
        if self.storage_file.exists():
            with open(self.storage_file, "r") as f:
                self._events = json.load(f)
        else:
            self._events = []

    def _save_events(self):
        with open(self.storage_file, "w") as f:
            json.dump(self._events, f, indent=2)

    async def add_event(self, title: str, start_time: str, end_time: str, description: str = "") -> str:
        """Add a calendar event."""
        event = {
            "id": f"event_{len(self._events)}",
            "title": title,
            "start": start_time,
            "end": end_time,
            "description": description,
        }
        self._events.append(event)
        self._save_events()
        return f"已添加日程: {title} ({start_time} - {end_time})"

    async def list_events(self, date: Optional[str] = None) -> str:
        """List calendar events."""
        if not self._events:
            return "暂无日程"

        filtered = self._events
        if date:
            filtered = [e for e in self._events if e["start"].startswith(date)]

        lines = [f"- {e['title']}: {e['start']} - {e['end']}" for e in filtered]
        return "\n".join(lines) if lines else "当天无日程"
