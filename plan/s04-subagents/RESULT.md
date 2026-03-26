# s04: Subagents - 实现效果

## 核心功能

### SubagentManager（agent/core/subagent.py）

```python
class SubagentManager:
    """管理多个子代理，每个子代理有独立的消息历史"""

    def __init__(self):
        self._subagents: dict[str, Subagent] = {}

    def spawn(self, name: str, role: str, tools: list[str]) -> str:
        """派生新的子代理，返回 subagent_id"""
        subagent_id = str(uuid.uuid4())[:12]
        subagent = Subagent(
            id=subagent_id,
            name=name,
            role=role,
            tools=tools,
        )
        self._subagents[subagent_id] = subagent
        return subagent_id

    def send(self, subagent_id: str, message: str) -> None:
        """发送消息到子代理的收件箱"""

    def receive(self, subagent_id: str) -> list[Message]:
        """接收子代理的所有消息"""

    def terminate(self, subagent_id: str) -> None:
        """终止子代理"""

    def inject_agent(self, subagent_id: str, agent: Agent) -> None:
        """将 Agent 实例注入子代理"""

    def get_agent(self, subagent_id: str) -> Optional[Agent]:
        """获取子代理的 Agent 实例"""
```

### Subagent 数据结构

```python
@dataclass
class Subagent:
    id: str
    name: str
    role: str
    tools: list[str]
    messages: list[Message] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    terminated: bool = False
```

### 关键设计

- **独立消息空间**: 每个子代理维护自己的 `messages[]`
- **隔离执行**: 子代理之间不共享上下文
- **主对话清洁**: 主 Agent 只保留子代理的结果，不暴露内部细节
- **send/receive 机制**: 通过消息传递而非共享状态通信

## 集成到 Agent Loop

### dispatch.py 注册 SpawnTool

```python
@classmethod
def from_directory(cls, tool_dir: str, subagent_manager=None) -> "DispatchMap":
    # ...
    if subagent_manager:
        from agent.tools.builtin.spawn import SpawnTool
        dispatch.register(SpawnTool(subagent_manager))
    return dispatch
```

### main.py 初始化 SubagentManager

```python
subagent_manager = SubagentManager()
dispatch = DispatchMap.from_directory("agent/tools/builtin", subagent_manager)
tools = dispatch.list_tools()
```

### SpawnTool 使用

```python
# 派生子代理
spawn(name="reviewer", role="code reviewer", tools=["read", "glob"])
```

## 验证

```bash
python -c "from agent.core.subagent import SubagentManager; print('OK')"
# Output: OK
```
