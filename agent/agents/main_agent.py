"""Main Coordinator Agent - routes tasks to specialized agents."""

import re
from dataclasses import dataclass, field
from typing import Optional, TYPE_CHECKING

from agent.core.loop import Agent
from agent.llm.deepseek import DeepSeekClient

if TYPE_CHECKING:
    from agent.agents.search_agent import SearchAgent
    from agent.agents.schedule_agent import ScheduleAgent
    from agent.agents.document_agent import DocumentAgent
    from agent.agents.email_agent import EmailAgent
    from agent.agents.file_agent import FileAgent
    from agent.agents.calendar_agent import CalendarAgent


@dataclass
class MainAgent:
    """Main coordinator agent that routes user requests to specialized agents."""

    llm_client: DeepSeekClient
    search_agent: Optional["SearchAgent"] = None
    schedule_agent: Optional["ScheduleAgent"] = None
    document_agent: Optional["DocumentAgent"] = None
    email_agent: Optional["EmailAgent"] = None
    file_agent: Optional["FileAgent"] = None
    calendar_agent: Optional["CalendarAgent"] = None
    system_prompt: str = """你是一个个人办公助手，协调各个专业 Agent 来完成任务。
    可用 Agent:
    - search: 网络搜索
    - schedule: 日程和提醒管理
    - document: 文档生成(PPT/Word/Excel)
    - email: 邮件管理
    - file: 文件整理

    当用户提出请求时，分析需求并将任务分发到相应的 Agent。"""

    async def process(self, user_message: str) -> str:
        """Process user message and coordinate agent response."""
        msg_lower = user_message.lower()

        # Route to SearchAgent: 搜索, 查找, 找
        if any(kw in msg_lower for kw in ["搜索", "查找", "找", "search", "查找"]):
            if self.search_agent:
                # Extract query - remove routing keywords
                query = re.sub(r"(帮我|请|帮我找|搜索|查找)[\s]*", "", user_message)
                result = await self.search_agent.search(query)
                return f"[SearchAgent] {result}"

        # Route to ScheduleAgent: 提醒, 日程提醒
        if any(kw in msg_lower for kw in ["提醒", "日程提醒"]):
            if self.schedule_agent:
                # Extract reminder content
                content = re.sub(r".*(提醒我|设置提醒|提醒)[\s]*", "", user_message)
                result = await self.schedule_agent.schedule_reminder(content)
                return f"[ScheduleAgent] {result}"

        # Route to CalendarAgent: 日程, 会议, 安排, calendar
        if any(kw in msg_lower for kw in ["日程", "会议", "安排", "calendar", "日历"]):
            if self.calendar_agent:
                # Check if user wants to list events
                if "列出" in msg_lower or "查看" in msg_lower or "list" in msg_lower:
                    result = await self.calendar_agent.list_events()
                    return f"[CalendarAgent] {result}"
                # Otherwise try to add an event
                # Simple pattern: "添加日程: title at time"
                match = re.search(r"(.+)在(.+?)(?:到|-)(.+)", user_message)
                if match:
                    title, start, end = match.groups()
                    result = await self.calendar_agent.add_event(title.strip(), start.strip(), end.strip())
                    return f"[CalendarAgent] {result}"

        # Route to DocumentAgent: PPT, 演示, 文档, Word, Excel
        if any(kw in msg_lower for kw in ["ppt", "演示", "文档", "word", "excel", "生成文档"]):
            if self.document_agent:
                if "ppt" in msg_lower or "演示" in msg_lower:
                    return "[DocumentAgent] 请提供PPT标题和内容，我将帮您生成。"
                elif "excel" in msg_lower or "表格" in msg_lower:
                    return "[DocumentAgent] 请提供Excel的表头和数据，我将帮您生成。"
                elif "word" in msg_lower or "文档" in msg_lower or "docx" in msg_lower:
                    return "[DocumentAgent] 请提供文档标题和内容，我将帮您生成。"

        # Route to EmailAgent: 邮件, 发邮件, 收邮件
        if any(kw in msg_lower for kw in ["邮件", "发邮件", "收邮件", "email"]):
            if self.email_agent:
                if "发" in msg_lower or "send" in msg_lower:
                    return "[EmailAgent] 请提供收件人、主题和正文，我将帮您发送邮件。"
                else:
                    result = await self.email_agent.read_emails()
                    return f"[EmailAgent] {result}"

        # Route to FileAgent: 整理文件, 文件管理, 文件整理
        if any(kw in msg_lower for kw in ["整理文件", "文件管理", "文件整理", "organize"]):
            if self.file_agent:
                # Extract directory
                dir_match = re.search(r"([A-Za-z]:[\\\/]|[\\\/].*?)(?:$|\s)", user_message)
                source_dir = dir_match.group(1) if dir_match else "."
                result = await self.file_agent.organize_files(source_dir)
                return f"[FileAgent] {result}"

        # Default: use LLM to generate response
        return f"收到消息: {user_message}\n\n正在协调相关 Agent 处理..."

    async def close(self):
        """Close the LLM client."""
        if self.llm_client:
            await self.llm_client.close()
