# s07: Tasks - 实现效果

## 核心功能

### TaskManager（agent/core/tasks.py）

文件存储的任务依赖图管理器，支持拓扑排序执行。

```python
class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    depends_on: list[str] = field(default_factory=list)
    assigned_to: Optional[str] = None

class TaskManager:
    def __init__(self, state_dir: str):
        self._store = FileStore(state_dir)

    def create_task(self, task_create: TaskCreate) -> str:
        """创建新任务，返回任务ID"""

    def get_task(self, task_id: str) -> Task:
        """根据ID获取任务"""

    def update_task(self, task_id: str, update: TaskUpdate) -> None:
        """更新任务属性"""

    def list_tasks(self, status: Optional[TaskStatus] = None) -> list[Task]:
        """列出任务，可按状态过滤"""

    def add_dependency(self, task_id: str, depends_on: str) -> None:
        """添加依赖关系，自动检测循环依赖"""

    def get_ready_tasks(self) -> list[Task]:
        """获取就绪任务（无依赖或依赖已完成）"""

    def get_dependent_tasks(self, task_id: str) -> list[Task]:
        """获取依赖给定任务的所有任务"""
```

### 内置任务工具

| 工具 | 功能 |
|------|------|
| `task_create` | 创建任务 (title, description, priority, depends_on, assigned_to) |
| `task_update` | 更新任务 (task_id, title, description, status, priority, assigned_to) |
| `task_list` | 列出任务 (可选 status 过滤) |
| `task_depends` | 添加任务依赖 (task_id, depends_on) |

## 集成

### main.py 初始化

```python
from agent.core.tasks import TaskManager

# Initialize TaskManager and wire it to task tools (s07: Tasks)
task_manager = TaskManager(state_dir=".agent_tasks")
from agent.tools.builtin.task_create import set_task_manager as set_task_create_manager
from agent.tools.builtin.task_update import set_task_manager as set_task_update_manager
from agent.tools.builtin.task_list import set_task_manager as set_task_list_manager
from agent.tools.builtin.task_depends import set_task_manager as set_task_depends_manager

set_task_create_manager(task_manager)
set_task_update_manager(task_manager)
set_task_list_manager(task_manager)
set_task_depends_manager(task_manager)
```

### dispatch.py 注册

```python
# Import and register task tools (s07: Tasks)
from agent.tools.builtin.task_create import TaskCreateTool
from agent.tools.builtin.task_update import TaskUpdateTool
from agent.tools.builtin.task_list import TaskListTool
from agent.tools.builtin.task_depends import TaskDependsTool

dispatch.register(TaskCreateTool())
dispatch.register(TaskUpdateTool())
dispatch.register(TaskListTool())
dispatch.register(TaskDependsTool())
```

## 效果

支持文件持久化的任务依赖图，具备：
- 任务创建、查询、更新、删除
- 依赖关系管理（自动循环检测）
- 就绪任务获取（拓扑排序）
- 优先级和状态跟踪

## 验证

```bash
python -c "from agent.core.tasks import TaskManager; tm = TaskManager('.test_state'); print('OK')"
python -c "from agent.tools.builtin.task_create import TaskCreateTool; print('OK')"
```
