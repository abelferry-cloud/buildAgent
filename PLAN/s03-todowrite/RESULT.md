# s03: TodoWrite - 实现效果

## 核心功能

### TodoManager（agent/core/todo.py）

```python
class TodoManager:
    def __init__(self):
        self._todos: list[TodoItem] = []

    def add(self, content: str, status: str = "pending") -> TodoItem:
        """添加待办"""
        todo = TodoItem(content=content, status=status)
        self._todos.append(todo)
        return todo

    def list(self) -> list[TodoItem]:
        """列出所有待办"""
        return self._todos

    def done(self, todo_id: str) -> bool:
        """标记完成"""
        for todo in self._todos:
            if todo.id == todo_id:
                todo.status = "completed"
                return True
        return False
```

### 内置 Todo 工具

| 工具 | 功能 |
|------|------|
| `todo_add` | 添加新待办 |
| `todo_list` | 列出所有待办 |
| `todo_done` | 标记待办完成 |

## 待实现

- Nag Reminder: 3 轮无 todo 操作时自动提醒
- Single `in_progress`: 只能有一个进行中的任务
