# s01: Agent Loop - 实现效果

## 核心功能

`agent/core/loop.py` 中的 `Agent` 类实现了最小 Agent 内核：

### 1. While 循环 + 单工具执行

```python
class Agent:
    def __init__(self, tools: list[Tool], model: str = "llama3.2", ...):
        self.tools = {t.name: t for t in tools}
        self.max_iterations = max_iterations

    async def run(self, initial_message: str) -> str:
        """主循环 - 执行直到 done"""
        while self._iteration_count < self.max_iterations:
            response = await self.step()
            if response.done:
                break
        return "\n\n".join(all_messages)
```

### 2. 消息历史管理

```python
@dataclass
class Message:
    role: str  # "user", "assistant", "system", "tool"
    content: str
    tool_calls: Optional[list[ToolCall]] = None
    tool_call_id: Optional[str] = None
```

### 3. 工具执行

```python
def execute_tool(self, tool_call: ToolCall) -> ToolResult:
    tool = self.tools.get(tool_call.name)
    if not tool:
        return ToolResult(error=f"Tool '{tool_call.name}' not found")
    return tool.execute(**tool_call.arguments)
```

## 验证

运行 `pytest` 测试 Agent Loop 的核心功能。
