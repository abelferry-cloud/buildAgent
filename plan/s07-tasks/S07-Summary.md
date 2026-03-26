# S07: Tasks - 总结

## 核心理念

> Task dependency graph with topological sorting and execution ordering

## 核心原理

S07 实现了基于文件持久化的任务管理系统，支持任务依赖图和拓扑排序。

### 核心功能

- **CRUD 操作** - 创建、读取、更新、删除任务
- **依赖管理** - `add_dependency()` 添加依赖关系，支持循环检测
- **就绪任务** - `get_ready_tasks()` 返回所有依赖都已完成的任务
- **拓扑排序** - 自动计算任务执行顺序

### 依赖循环检测

使用 DFS 算法检测是否会形成循环：
```python
def _would_create_cycle(task_id, depends_on):
    # 如果添加这条边会导致从 depends_on 出发能到达 task_id
    # 则说明会形成循环
```

## 关键类/组件

| 名称 | 文件 | 职责 |
|------|------|------|
| `TaskStatus` | `agent/core/tasks.py` | 任务状态枚举 (PENDING, IN_PROGRESS, COMPLETED, BLOCKED) |
| `Task` | `agent/core/tasks.py` | 任务数据结构 |
| `TaskManager` | `agent/core/tasks.py` | 任务生命周期和依赖管理 |

## 涉及的文件

### 核心文件
- `agent/core/tasks.py` - TaskManager 实现

### 工具文件
- `agent/tools/builtin/task_create.py` - TaskCreateTool
- `agent/tools/builtin/task_update.py` - TaskUpdateTool
- `agent/tools/builtin/task_list.py` - TaskListTool
- `agent/tools/builtin/task_depends.py` - TaskDependsTool

### 状态管理
- `agent/state/filestore.py` - FileStore，文件持久化

## 与 main.py 的集成

```python
from agent.core.tasks import TaskManager

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

## 工具列表

| 工具名 | 类 | 功能 |
|--------|-----|------|
| `task_create` | TaskCreateTool | 创建任务（title, description, priority, depends_on） |
| `task_update` | TaskUpdateTool | 更新任务属性 |
| `task_list` | TaskListTool | 列出任务（支持状态过滤） |
| `task_depends` | TaskDependsTool | 添加任务依赖关系 |

## Task 数据结构

```python
@dataclass
class Task:
    id: str
    title: str
    description: str
    status: TaskStatus
    priority: int
    created_at: float
    updated_at: float
    depends_on: list[str]   # 依赖的任务 ID 列表
    assigned_to: str | None
```

## 架构图

```
┌─────────────────────────────────────┐
│          TaskManager                │
│  ┌───────────────────────────────┐  │
│  │ _state_dir: str              │  │
│  │ _store: FileStore             │  │
│  │ _tasks: dict[str, Task]      │  │
│  └───────────────────────────────┘  │
│  create_task() │ add_dependency() │
│  get_ready_tasks() │ get_dependent_tasks()
└─────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────┐
│      .agent_tasks/ (持久化目录)      │
│  ┌───────────────────────────────┐  │
│  │ tasks.jsonl                  │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘

依赖图示例:
  Task A
   │ │
   ▼ │
  Task B ──► Task C
             │
             ▼
            Task D (等待 B, C 完成)
```
