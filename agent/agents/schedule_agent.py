"""Schedule Agent - handles scheduling and reminders."""

from agent.skills.schedule_reminder import ScheduleReminderTool


class ScheduleAgent:
    """Agent specialized in scheduling and reminders."""

    def __init__(self):
        self.tool = ScheduleReminderTool()

    async def schedule_reminder(self, message: str, trigger_time: str = None, cron: str = None) -> str:
        """Schedule a reminder."""
        result = self.tool.execute(message=message, trigger_time=trigger_time, cron=cron)
        if result.error:
            return f"设置提醒失败: {result.error}"
        return result.output
