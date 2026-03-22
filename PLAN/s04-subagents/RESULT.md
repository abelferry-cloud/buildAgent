# s04: Subagents - 实现效果

## 核心功能

### SubagentManager（agent/core/subagent.py）

```python
class SubagentManager:
    """管理多个子代理，每个子代理有独立的消息历史"""

    def __init__(self):
        self._subagents: dict[str, Agent] = {}

    def spawn(self, name: str, tools: list[Tool], **kwargs) -> Agent:
        """派生新的子代理"""
        agent = Agent(tools=tools, **kwargs)
        self._subagents[name] = agent
        return agent

    def get(self, name: str) -> Optional[Agent]:
        """获取子代理"""
        return self._subagents.get(name)
```

### 关键设计

- **独立消息空间**: 每个子代理维护自己的 `messages[]`
- **隔离执行**: 子代理之间不共享上下文
- **主对话清洁**: 主 Agent 只保留子代理的结果，不暴露内部细节
