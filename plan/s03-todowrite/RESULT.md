# s03: TodoWrite - 实现效果

## 核心功能

### TodoManager（agent/core/todo.py）

```python
class TodoManager:
    NAG_THRESHOLD = 3  # Nag after 3 rounds without todo tool usage

    def __init__(self):
        self._todos: dict[str, Todo] = {}
        self._rounds_since_todo: int = 0

    def add(self, task: str, priority: int = 0) -> str:
        """添加待办"""
        todo_id = str(uuid.uuid4())[:8]
        todo = Todo(id=todo_id, task=task, priority=priority)
        self._todos[todo_id] = todo
        self._rounds_since_todo = 0  # Reset nag counter on todo action
        return todo_id

    def list(self) -> List[Todo]:
        """列出所有待办（按优先级和创建时间排序）"""
        todos = [t for t in self._todos.values() if not t.done]
        todos.sort(key=lambda t: (-t.priority, t.created_at))
        return todos

    def done(self, todo_id: str) -> bool:
        """标记完成"""
        ...

    def start(self, todo_id: str) -> bool:
        """标记进行中（只能有一个进行中的任务）"""
        ...

    def increment_round(self) -> None:
        """增量回合计数器（当没有使用 todo 工具时调用）"""
        self._rounds_since_todo += 1

    def should_nag(self) -> bool:
        """检查是否应该注入提醒"""
        return self._rounds_since_todo >= self.NAG_THRESHOLD
```

### 内置 Todo 工具

| 工具 | 文件 | 功能 |
|------|------|------|
| `todo_add` | `builtin/todo_add.py` | 添加新待办 |
| `todo_list` | `builtin/todo_list.py` | 列出所有待办 |
| `todo_done` | `builtin/todo_done.py` | 标记待办完成 |
| `todo_start` | `builtin/todo_start.py` | 标记待办进行中 |

## Nag Reminder 机制

### 实现原理

1. **回合计数器**: `TodoManager._rounds_since_todo` 追踪自上次使用 todo 工具以来的回合数
2. **阈值检测**: 当计数器达到 `NAG_THRESHOLD`（3）时，`should_nag()` 返回 `True`
3. **提醒注入**: 在 `_llm_step()` 中构建系统消息时，如果 `should_nag()` 为 `True`，则注入 `<reminder>Update your todos.</reminder>`

### 计数器更新逻辑

```python
# Agent._llm_step() 中的更新逻辑:
if tool_calls:
    # 执行工具...
    # 如果使用了 todo 工具，重置计数器
    if self._todo_manager:
        self._todo_manager._rounds_since_todo = 0
else:
    # 没有工具调用，计数器 +1
    if self._todo_manager:
        self._todo_manager.increment_round()
```

### 单个 in_progress 约束

`TodoManager.start()` 方法确保只有一个任务可以处于 `in_progress` 状态：

```python
def start(self, todo_id: str) -> bool:
    """Mark a todo as in_progress. Only one todo can be in_progress at a time."""
    # 清除任何现有的 in_progress todo
    for t in self._todos.values():
        if t.in_progress and t.id != todo_id:
            t.in_progress = False
    todo.in_progress = True
```

## 集成到 Agent Loop

### TodoManager 初始化（main.py）

```python
# Initialize TodoManager and wire it to todo tools (s03)
todo_manager = TodoManager()
from agent.tools.builtin.todo_add import set_todo_manager as set_todo_add_manager
from agent.tools.builtin.todo_list import set_todo_manager as set_todo_list_manager
from agent.tools.builtin.todo_done import set_todo_manager as set_todo_done_manager
from agent.tools.builtin.todo_start import set_todo_manager as set_todo_start_manager

set_todo_add_manager(todo_manager)
set_todo_list_manager(todo_manager)
set_todo_done_manager(todo_manager)
set_todo_start_manager(todo_manager)

agent = Agent(..., todo_manager=todo_manager)
```

### Nag 提醒注入（loop.py）

```python
async def _llm_step(self, tool_descriptions: str) -> AgentResponse:
    # ...
    # Inject nag reminder if threshold reached (s03: TodoWrite)
    if self._todo_manager and self._todo_manager.should_nag():
        nag_msg = self._todo_manager.get_nag_message()
        system_with_tools = f"{system_with_tools}\n\n{nag_msg}"
    # ...
```
