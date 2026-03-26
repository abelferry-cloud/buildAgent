"""Schedule reminder skill using APScheduler."""

from datetime import datetime, timedelta
from typing import Optional
import json
from pathlib import Path

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
except ImportError:
    AsyncIOScheduler = None

from agent.tools.base import Tool, ToolResult


class ScheduleReminderTool(Tool):
    """Schedule a reminder or timed task."""

    name = "schedule_reminder"
    description = "Schedule a reminder or notification at a specific time."

    def __init__(self, storage_file: str = ".agent/reminders.json"):
        super().__init__()
        self.storage_file = Path(storage_file)
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self.scheduler = AsyncIOScheduler() if AsyncIOScheduler else None
        self._load_reminders()

    def _load_reminders(self):
        """Load reminders from storage."""
        if self.storage_file.exists():
            with open(self.storage_file, "r") as f:
                self._reminders = json.load(f)
        else:
            self._reminders = []

    def _save_reminders(self):
        """Save reminders to storage."""
        with open(self.storage_file, "w") as f:
            json.dump(self._reminders, f, indent=2, default=str)

    def execute(
        self,
        message: str,
        trigger_time: Optional[str] = None,
        cron: Optional[str] = None,
    ) -> ToolResult:
        """Schedule a reminder."""
        if not self.scheduler:
            return ToolResult(
                output="",
                error="APScheduler not installed. Run: pip install apscheduler"
            )

        reminder = {
            "id": f"reminder_{len(self._reminders)}",
            "message": message,
            "trigger_time": trigger_time,
            "cron": cron,
            "created_at": datetime.now().isoformat(),
        }

        self._reminders.append(reminder)
        self._save_reminders()

        # Add job to scheduler
        if trigger_time:
            dt = datetime.fromisoformat(trigger_time)
            self.scheduler.add_job(
                func=self._send_notification,
                trigger_date=dt,
                args=[message],
                id=reminder["id"],
            )
        elif cron:
            # Parse simple cron: "hour,minute,day_of_week"
            parts = cron.split(",")
            if len(parts) == 3:
                self.scheduler.add_job(
                    func=self._send_notification,
                    trigger=CronTrigger(
                        hour=parts[0], minute=parts[1], day_of_week=parts[2]
                    ),
                    args=[message],
                    id=reminder["id"],
                )

        if not self.scheduler.running:
            self.scheduler.start()

        return ToolResult(output=f"已设置提醒: {message}")

    def _send_notification(self, message: str):
        """Send notification (placeholder - integrate with notification system)."""
        print(f"[REMINDER] {message}")
