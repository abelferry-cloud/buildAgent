# s07: Tasks - 实现效果

## 核心功能

### TaskGraph（agent/core/tasks.py）

```python
@dataclass
class Task:
    id: str
    content: str
    status: str = "pending"  # pending, in_progress, completed
    dependencies: list[str] = field(default_factory=list)

class TaskGraph:
    def __init__(self):
        self._tasks: dict[str, Task] = {}

    def create(self, task_id: str, content: str, dependencies: list[str] = None) -> Task:
        """创建任务"""
        task = Task(id=task_id, content=content, dependencies=dependencies or [])
        self._tasks[task_id] = task
        return task

    def get_ready_tasks(self) -> list[Task]:
        """获取就绪任务（无依赖或依赖已完成）"""
        ready = []
        for task in self._tasks.values():
            if task.status == "pending":
                deps_done = all(self._tasks[d].status == "completed" for d in task.dependencies)
                if deps_done:
                    ready.append(task)
        return ready

    def execute_all(self) -> list[Task]:
        """拓扑排序执行所有任务"""
        # 按依赖顺序返回任务列表
        pass
```

### 内置任务工具

| 工具 | 功能 |
|------|------|
| `task_create` | 创建任务 |
| `task_update` | 更新任务状态 |
| `task_list` | 列出任务 |
| `task_depends` | 设置任务依赖 |
