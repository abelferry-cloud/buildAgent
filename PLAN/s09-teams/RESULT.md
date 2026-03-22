# s09: Agent Teams - 实现效果

## 核心功能

### TeammateManager（agent/core/teams.py）

```python
class TeammateManager:
    """管理多个持久化队友代理"""

    def __init__(self, team_id: str, mailbox_dir: str):
        self._team_id = team_id
        self._mailbox_dir = Path(mailbox_dir)
        self._teammates: dict[str, TeammateInfo] = {}
        self._mailboxes: dict[str, Mailbox] = {}
        self._agents: dict[str, Agent] = {}

    def create_teammate(self, name: str, role: str, agent_config: AgentConfig) -> str:
        """创建新队友"""

    def send_message(self, to: str, message: str, protocol: ProtocolType = ProtocolType.DIRECT, from_: str | None = None) -> str:
        """发送消息给队友"""

    def read_mailbox(self, teammate_name: str) -> list[Message]:
        """读取队友收件箱"""

    def get_teammate_status(self, name: str) -> TeammateStatus:
        """获取队友状态"""

    def list_teammates(self) -> list[TeammateInfo]:
        """列出所有队友"""

    def broadcast(self, message: str, from_: str | None = None) -> list[str]:
        """广播消息给所有队友"""
```

### Mailbox（agent/state/mailbox.py）

```python
class Mailbox:
    """基于文件的异步邮箱"""

    def __init__(self, mailbox_path: str):
        self._path = Path(mailbox_path)
        self._inbox_path = self._path / "inbox.jsonl"
        self._outbox_path = self._path / "outbox.jsonl"

    def send(self, message: Message) -> None:
        """发送消息到 outbox"""

    def receive_all(self) -> list[Message]:
        """接收所有未读消息"""

    def mark_read(self, message_ids: list[str]) -> None:
        """标记消息为已读"""
```

### 内置团队工具

| 工具 | 功能 |
|------|------|
| `team_send` | 发送消息给队友 |
| `team_broadcast` | 广播消息 |
| `team_list` | 列出团队 |
| `team_status` | 查看状态 |

## 集成

### main.py 初始化

```python
from agent.core.teams import TeammateManager

# Initialize TeammateManager and wire it to team tools (s09: Agent Teams)
teammate_manager = TeammateManager(team_id="main", mailbox_dir=".mailbox")
from agent.tools.builtin.team_send import set_teammate_manager as set_team_send_manager
from agent.tools.builtin.team_broadcast import set_teammate_manager as set_team_broadcast_manager
from agent.tools.builtin.team_list import set_teammate_manager as set_team_list_manager
from agent.tools.builtin.team_status import set_teammate_manager as set_team_status_manager

set_team_send_manager(teammate_manager)
set_team_broadcast_manager(teammate_manager)
set_team_list_manager(teammate_manager)
set_team_status_manager(teammate_manager)
```

### dispatch.py 注册

```python
# Import and register team tools (s09: Agent Teams)
from agent.tools.builtin.team_send import TeamSendTool
from agent.tools.builtin.team_broadcast import TeamBroadcastTool
from agent.tools.builtin.team_list import TeamListTool
from agent.tools.builtin.team_status import TeamStatusTool

dispatch.register(TeamSendTool())
dispatch.register(TeamBroadcastTool())
dispatch.register(TeamListTool())
dispatch.register(TeamStatusTool())
```

## 验证

```bash
python -c "from agent.core.teams import TeammateManager; print('OK')"
python -c "from agent.tools.builtin.team_send import TeamSendTool; print('OK')"
```
