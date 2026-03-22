# s09: Agent Teams - 实现效果

## 核心功能

### TeammateManager（agent/core/teams.py）

```python
class TeammateManager:
    """管理多个持久化队友代理"""

    def __init__(self, mailbox_dir: str = ".mailbox"):
        self._teammates: dict[str, Agent] = {}
        self._mailbox = Mailbox(mailbox_dir)

    async def send(self, to: str, message: str) -> bool:
        """发送消息给队友"""
        return self._mailbox.send(to, message)

    async def broadcast(self, message: str) -> None:
        """广播消息给所有队友"""
        for name in self._teammates:
            await self.send(name, message)

    async def receive(self, agent_name: str) -> list[Message]:
        """接收消息"""
        return self._mailbox.receive(agent_name)

    def add_teammate(self, name: str, agent: Agent) -> None:
        """添加队友"""
        self._teammates[name] = agent
```

### Mailbox（agent/state/mailbox.py）

```python
class Mailbox:
    """基于文件的异步邮箱"""

    def __init__(self, base_dir: str):
        self.inbox = f"{base_dir}/inbox.jsonl"
        self.outbox = f"{base_dir}/outbox.jsonl"

    def send(self, to: str, message: str) -> bool:
        """发送消息到 outbox"""
        entry = {"to": to, "message": message, "timestamp": time.time()}
        append_jsonl(self.outbox, entry)
        return True

    def receive(self, agent_name: str) -> list[Message]:
        """从 inbox 读取消息"""
        return read_jsonl(self.inbox)
```

### 内置团队工具

| 工具 | 功能 |
|------|------|
| `team_send` | 发送消息给队友 |
| `team_broadcast` | 广播消息 |
| `team_list` | 列出团队 |
| `team_status` | 查看状态 |

### Task Board 工具

| 工具 | 功能 |
|------|------|
| `board_post` | 发布任务 |
| `board_poll` | 轮询任务 |
| `board_claim` | 认领任务 |
| `board_complete` | 完成任务 |
