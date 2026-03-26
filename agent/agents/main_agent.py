"""Main Coordinator Agent - routes tasks to specialized agents."""

import asyncio
from dataclasses import dataclass
from typing import Optional

from agent.core.loop import Agent
from agent.llm.deepseek import DeepSeekClient


@dataclass
class MainAgent:
    """Main coordinator agent that routes user requests to specialized agents."""

    llm_client: DeepSeekClient
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
        # For now, echo back with acknowledgment
        # Later: parse intent, call specialized agents
        return f"收到消息: {user_message}\n\n正在协调相关 Agent 处理..."

    async def close(self):
        """Close the LLM client."""
        if self.llm_client:
            await self.llm_client.close()
