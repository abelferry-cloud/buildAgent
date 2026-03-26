# s11: Autonomous Agents - 实现效果

## 核心功能

### TaskBoard（agent/core/autonomous.py）

```python
class TaskBoard:
    """基于文件的公共任务板，支持轮询协调"""

    def __init__(self, board_file: str):
        self._board_file = board_file
        self._tasks: dict[str, BoardTask] = {}
        self._workers: set[str] = set()

    def post_task(self, task: BoardTask | None = None, title: str = "", ...) -> str:
        """发布任务"""

    def claim_task(self, task_id: str, worker: str) -> bool:
        """认领任务"""

    def complete_task(self, task_id: str, result: dict | None = None) -> bool:
        """完成任务"""

    def poll(self, worker: str, timeout: float = 30.0) -> BoardTask | None:
        """轮询可用任务（自动认领）"""

    def get_board_state(self) -> BoardState:
        """获取任务板状态"""
```

### AutonomousGovernor

```python
class AutonomousGovernor:
    """自主代理治理器"""

    def __init__(self, agent: Agent, config: GovernorConfig | None = None):
        self._config = config or GovernorConfig()

    def should_continue(self) -> bool:
        """检查是否应该继续执行"""

    def check_timeouts(self) -> list[TimeoutAction]:
        """检查超时条件"""

    def apply_timeout_action(self, task_id: str, action: TimeoutAction) -> dict:
        """应用超时动作"""
```

### 内置任务板工具

| 工具 | 功能 |
|------|------|
| `board_post` | 发布任务到任务板 |
| `board_poll` | 轮询可用任务（自动认领） |
| `board_claim` | 认领特定任务 |
| `board_complete` | 完成任务 |

## 集成

### main.py 初始化

```python
from agent.core.autonomous import TaskBoard

# Initialize TaskBoard and wire it to board tools (s11: Autonomous Agents)
task_board = TaskBoard(board_file=".taskboard.json")
from agent.tools.builtin.board_post import set_board as set_board_post
# ... set for all board tools
```

### dispatch.py 注册

```python
# Import and register board tools (s11: Autonomous Agents)
from agent.tools.builtin.board_post import BoardPostTool
from agent.tools.builtin.board_poll import BoardPollTool
from agent.tools.builtin.board_claim import BoardClaimTool
from agent.tools.builtin.board_complete import BoardCompleteTool

dispatch.register(BoardPostTool())
dispatch.register(BoardPollTool())
dispatch.register(BoardClaimTool())
dispatch.register(BoardCompleteTool())
```

## 验证

```bash
python -c "from agent.core.autonomous import TaskBoard, AutonomousGovernor; print('OK')"
python -c "from agent.tools.builtin.board_post import BoardPostTool; print('OK')"
```
